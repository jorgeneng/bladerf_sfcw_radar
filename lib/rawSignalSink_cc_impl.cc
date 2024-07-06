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
rawSignalSink_cc::sptr rawSignalSink_cc::make()
{
    return gnuradio::make_block_sptr<rawSignalSink_cc_impl>();
}


/*
 * The private constructor
 */
rawSignalSink_cc_impl::rawSignalSink_cc_impl()
    : gr::sync_block("rawSignalSink_cc",
                     gr::io_signature::make(
                         2 /* min inputs */, 2 /* max inputs */, sizeof(input_type)),
                     gr::io_signature::make(0, 0, 0)),
    d_itemsize(sizeof(input_type))
{
}

/*
 * Our virtual destructor.
 */
rawSignalSink_cc_impl::~rawSignalSink_cc_impl() {}

int rawSignalSink_cc_impl::work(int noutput_items,
                                gr_vector_const_void_star& input_items,
                                gr_vector_void_star& output_items)
{
    const char* refbuf = (const char*)(input_items[0]);
    const char* rxbuf = (const char*)(input_items[1]);

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
                std::cout << "get a new scan tag, idx: " << N << std::endl;
                if (d_ref_handle != nullptr){
                std::cout << "close previous file" << std::endl;
                    fclose(d_ref_handle);
                    d_ref_handle = nullptr;
                    d_rx_handle = nullptr;
                }
                std::cout << "create a new file to store the raw signals" << std::endl;
                std::string ref_filename = fmt::format("file_ref_{:d}.dat", scan_id);
                std::string rx_filename = fmt::format("file_rx_{:d}.dat", scan_id);
                std::string meta_filename = fmt::format("scan_meta_{:d}.json", scan_id);
                std::cout << ref_filename << ":" << rx_filename << ":" << meta_filename << std::endl;
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
    }

    // Tell runtime system how many output items we produced.
    return noutput_items;
}

} /* namespace sfcwRadar */
} /* namespace gr */
