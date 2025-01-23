/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "rawSignalSink_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <fcntl.h>

#ifdef O_BINARY
#define OUR_O_BINARY O_BINARY
#else
#define OUR_O_BINARY 0
#endif

// should be handled via configure
#ifdef O_LARGEFILE
#define OUR_O_LARGEFILE O_LARGEFILE
#else
#define OUR_O_LARGEFILE 0
#endif

namespace gr {
namespace sfcwRadar {

using input_type = gr_complex;
rawSignalSink_cc::sptr rawSignalSink_cc::make(std::string dir, 
                                             std::string prefix, 
                                             int num_steps,
                                             bladerf_frequency start_freq,
                                             bladerf_frequency freq_step,
                                             bladerf_gain tx_gain,
                                             bladerf_gain rx_gain,
                                             bladerf_gain ref_gain,
                                             int samp_rate,
                                             size_t burst_len,
                                             float cw_frequency,
                                             float cw_amplitude)
{
    return gnuradio::make_block_sptr<rawSignalSink_cc_impl>(dir, 
                                             prefix, 
                                             num_steps,
                                             start_freq,
                                             freq_step,
                                             tx_gain,
                                             rx_gain,
                                             ref_gain,
                                             samp_rate,
                                             burst_len,
                                             cw_frequency,
                                             cw_amplitude);
}


/*
 * The private constructor
 */
rawSignalSink_cc_impl::rawSignalSink_cc_impl(std::string dir, 
                                             std::string prefix, 
                                             int num_steps,
                                             bladerf_frequency start_freq,
                                             bladerf_frequency freq_step,
                                             bladerf_gain tx_gain,
                                             bladerf_gain rx_gain,
                                             bladerf_gain ref_gain,
                                             int samp_rate,
                                             size_t burst_len,
                                             float cw_frequency,
                                             float cw_amplitude)
    : gr::sync_block("rawSignalSink_cc",
                     gr::io_signature::make(
                         2 /* min inputs */, 2 /* max inputs */, sizeof(input_type)),
                     gr::io_signature::make(0, 0, 0)),
    d_itemsize(sizeof(input_type))
{
    /**
     * check if the provided dir exists
     * */
    struct stat info;
    if(stat(dir.c_str(), &info)!=0){
        std::cout << "cannot access " << dir << std::endl;
        return;
    }
    d_rx_dir_filename = dir+prefix+rx_suffix;
    d_ref_dir_fielname = dir+prefix+ref_suffix;
    std::cout << "rx samples will be stored to: " << d_rx_dir_filename << std::endl;
    std::cout << "ref samples will be stored to: " << d_ref_dir_fielname << std::endl;

    d_num_steps = num_steps;
    d_start_freq = start_freq;
    d_freq_step = freq_step;
    d_tx_gain = tx_gain;
    d_rx_gain = rx_gain;
    d_ref_gain = ref_gain;
    d_samp_rate = samp_rate;
    d_burst_len = burst_len;
    d_cw_frequency = cw_frequency;
    d_cw_amplitude = cw_amplitude;
}

/*
 * Our virtual destructor.
 */
rawSignalSink_cc_impl::~rawSignalSink_cc_impl() {}

int rawSignalSink_cc_impl::work(int noutput_items,
                                gr_vector_const_void_star& input_items,
                                gr_vector_void_star& output_items)
{
    const char* rxbuf = (const char*)(input_items[0]);
    const char* refbuf = (const char*)(input_items[1]);

    uint64_t start_N = nitems_read(0);
    uint64_t end_N = start_N + (uint64_t)(noutput_items);
    pmt::pmt_t tag_key = pmt::string_to_symbol("newScan");
    std::vector<tag_t> new_scan_tags;
    get_tags_in_range(new_scan_tags,0,start_N,end_N, tag_key);
    std::vector<tag_t>::iterator vitr = new_scan_tags.begin();

    uint64_t idx = 0;
    if(!new_scan_tags.empty()){
        //received at least one new scan tag
        while(vitr != new_scan_tags.end()){
            std::cout << (*vitr).key << std::endl;
            if(pmt::is_true((*vitr).value)){
                // for each valid new scan tag in the vector
                auto N = (*vitr).offset;
                idx = (N - start_N);
                //std::cout << "get a new scan tag, idx: " << N << std::endl;
                if (d_ref_handle != nullptr){
                //std::cout << "close previous file" << std::endl;
                    fclose(d_ref_handle);
                    d_ref_handle = nullptr;
                    d_rx_handle = nullptr;
                }
                //std::cout << "create a new file to store the raw signals" << std::endl;
                std::string ref_filename = d_ref_dir_fielname + std::to_string(scan_id) + ".dat";
                std::string rx_filename = d_rx_dir_filename + std::to_string(scan_id) + ".dat";
                //std::string ref_filename = fmt::format("file_ref_{:d}.dat", scan_id);
                //std::string rx_filename = fmt::format("file_rx_{:d}.dat", scan_id);
                std::string meta_filename = fmt::format("scan_meta_{:d}.json", scan_id);
                //std::cout << ref_filename << ":" << rx_filename << ":" << meta_filename << std::endl;
                scan_id ++ ;

                int ref_fd;
                if ((ref_fd = ::open(ref_filename.c_str(),
                                     O_WRONLY | O_CREAT | O_TRUNC | OUR_O_LARGEFILE |OUR_O_BINARY,
                                     0664)) < 0) {
                    return -1;
                } 

                if ((d_ref_handle = fdopen(ref_fd, "wb")) == NULL) {
                        ::close(ref_fd); // don't leak file descriptor if fdopen fails.
                } 

                int rx_fd;
                if ((rx_fd = ::open(rx_filename.c_str(),
                                     O_WRONLY | O_CREAT | O_TRUNC | OUR_O_LARGEFILE |OUR_O_BINARY,
                                     0664)) < 0) {
                    return -1;
                } 

                if ((d_rx_handle = fdopen(rx_fd, "wb")) == NULL) {
                        ::close(rx_fd); // don't leak file descriptor if fdopen fails.
                } 
            }
            vitr ++ ;
        }
    }

    if(d_ref_handle!=nullptr){
        int nwritten = 0;
        //size_t d_itemsize = sizeof(input_type); //gr_complex
        //write ref signal
        while(nwritten < noutput_items) {
            int count = std::fwrite(refbuf, d_itemsize, noutput_items - nwritten, d_ref_handle);
            if(count == 0) {
                if(std::ferror(d_ref_handle)) {
                    std::stringstream s;
                    s << "write ref signal failed with error " << fileno(d_ref_handle) << std::endl;
                    throw std::runtime_error(s.str());
                }else {
                    break;
                }
            }

            nwritten += count;
            refbuf += count * d_itemsize;
        } 
        //write rx signal
        nwritten = 0;
        while(nwritten < noutput_items) {
            int count = std::fwrite(rxbuf, d_itemsize, noutput_items - nwritten, d_rx_handle);
            if(count == 0) {
                if(std::ferror(d_rx_handle)) {
                    std::stringstream s;
                    s << "write rx signal failed with error " << fileno(d_rx_handle) << std::endl;
                    throw std::runtime_error(s.str());
                }else {
                    break;
                }
            }

            nwritten += count;
            rxbuf += count * d_itemsize;
        }
        //std::cout << "wrote: " << nwritten << std::endl;
    }

    // Tell runtime system how many output items we produced.
    return noutput_items;
}

} /* namespace sfcwRadar */
} /* namespace gr */
