/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "bladerfRadar_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>

namespace gr {
namespace sfcwRadar {

using input_type = gr_complex;
using output_type = gr_complex;
bladerfRadar_cc::sptr bladerfRadar_cc::make(bladerf_frequency start_freq,
                                            int num_steps,
                                            bladerf_frequency freq_step,
                                            int samp_rate,
                                            float rx_gain,
                                            float tx_gain,
                                            int tune_th)
{
    return gnuradio::make_block_sptr<bladerfRadar_cc_impl>(
        start_freq, num_steps, freq_step, samp_rate, rx_gain, tx_gain, tune_th);
}


/*
 * The private constructor
 */
bladerfRadar_cc_impl::bladerfRadar_cc_impl(bladerf_frequency start_freq, int num_steps, bladerf_frequency freq_step, int samp_rate, float rx_gain, float tx_gain, int tune_th)
    : gr::sync_block("bladerfRadar_cc",
                     gr::io_signature::make(
                         1 /* min inputs */, 1 /* max inputs */, sizeof(input_type)),
                     gr::io_signature::make(
                         2 /* min outputs */, 2 /*max outputs */, sizeof(output_type)))
{
    /**
     * Initialize the tags
     * */
    d_key = pmt::string_to_symbol("burst");
    d_value_true = pmt::from_bool(true);
    d_value_false = pmt::from_bool(false);
    d_srcid = pmt::string_to_symbol("bladerf_tx_rx");

    /**
     * save input parameters
     * */
    d_tune_th = tune_th;
    std::cout << "d_tune_th: " << d_tune_th << std::endl;
    d_start_freq = start_freq;
    d_freq_step = freq_step;
    d_currrent_freq = start_freq;
    d_max_freq = d_start_freq + d_freq_step * num_steps;
    std::cout << "start_freq: " << d_start_freq << std::endl;
    std::cout << "freq_step: " << d_freq_step << std::endl;
    std::cout << "max_freq: " << d_max_freq << std::endl;
    /**
     * Initialize the information used to identify the desired device
     * */
    bladerf_init_devinfo(&dev_info);
    std::cout << "dev_info" << &dev_info <<  std::endl;
    int status = bladerf_open_with_devinfo(&dev, &dev_info);
    if (status != 0){
        std::cerr << "Unable to open device: " << bladerf_strerror(status) << std::endl;
    }else{
        std::cout << "Device opend" << std::endl;
        char serial[BLADERF_SERIAL_LENGTH];
        //struct bladerf_version ver;
        if (bladerf_get_serial(dev, serial)==0){
            std::string strser(serial);
            std::cout << " Serial # " << strser << std::endl;
        }

        /**
         * Set up RX channel 0
         * */
        config.channel = BLADERF_CHANNEL_RX(0);
        config.frequency = start_freq;
        config.bandwidth = samp_rate/2;
        config.samplerate = samp_rate;
        config.gain = rx_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "RX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "RX channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        /**
         * Set up RX channel 1
         * RX channel 1 is connected with the TX using a spliter or directional decoupler to obtain reference signal
         * */
        config.channel = BLADERF_CHANNEL_RX(1);
        config.frequency = start_freq;
        config.bandwidth = samp_rate/2;
        config.samplerate = samp_rate;
        config.gain = 0;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "RX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "RX channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        /**
         * Set up TX channel 0
         * */
        config.channel = BLADERF_CHANNEL_TX(0);
        config.frequency = start_freq;
        config.bandwidth = samp_rate/2;
        config.samplerate = samp_rate;
        config.gain = tx_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "TX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "TX channel " << config.channel << ": configure_channel succed" << std::endl;

        }
        /* Initialize synch interface on RX and TX */
        status = init_sync(dev);
        if (status != 0) {
            fprintf(stderr, "Failed to enable RX: %s\n", bladerf_strerror(status));
        }
    }

   /* Set up constraints */
    int const alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
    set_alignment(std::max(1,alignment_multiple));
    set_max_noutput_items(buffer_size);
    set_output_multiple(2);
}

/*
 * Our virtual destructor.
 */
bladerfRadar_cc_impl::~bladerfRadar_cc_impl() {
    bladerf_close(dev);
}

int bladerfRadar_cc_impl::configure_channel(struct bladerf *dev, struct channel_config *c){
    int status;
    status = bladerf_set_frequency(dev, c->channel, c->frequency);
    if (status != 0) {
        fprintf(stderr, "Failed to set frequency = %u: %s\n", c->frequency,
        bladerf_strerror(status));
        return status;
    }
 
    status = bladerf_set_sample_rate(dev, c->channel, c->samplerate, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set samplerate = %u: %s\n", c->samplerate,
        bladerf_strerror(status));
        return status;
    }
    status = bladerf_set_bandwidth(dev, c->channel, c->bandwidth, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set bandwidth = %u: %s\n", c->bandwidth,
        bladerf_strerror(status));
        return status;
    } 
    status = bladerf_set_gain(dev, c->channel, c->gain);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain: %s\n", bladerf_strerror(status));
        return status;
    }
    status = bladerf_set_gain_mode(dev, c->channel, BLADERF_GAIN_MGC);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode: %s\n", bladerf_strerror(status));
        return status;
    }
    return status; 
}

int bladerfRadar_cc_impl::init_sync(struct bladerf *dev){
    int status;
 
 /* Configure both the device's X2 RX and X1 TX channels for use with the
 * synchronous
 * interface. SC16 Q11 samples *without* metadata are used. */
 
    status = bladerf_sync_config(dev, BLADERF_RX_X2, BLADERF_FORMAT_SC16_Q11,
                                num_buffers, buffer_size, num_transfers,
                                timeout_ms);
    if (status != 0) {
        fprintf(stderr, "Failed to configure RX sync interface: %s\n",
        bladerf_strerror(status));
        return status;
    }
 
    status = bladerf_sync_config(dev, BLADERF_TX_X1, BLADERF_FORMAT_SC16_Q11,
                                num_buffers, buffer_size, num_transfers,
                                timeout_ms);
    if (status != 0) {
        fprintf(stderr, "Failed to configure TX sync interface: %s\n",
        bladerf_strerror(status));
        return status;
    }

    status = bladerf_enable_module(dev, BLADERF_RX, true);
    if (status != 0) {
        std::cerr << "RX enable failed" << std::endl;
        return status;
    } 
    
    status = bladerf_enable_module(dev, BLADERF_TX, true);
    if (status != 0) {
        std::cerr << "TX enable failed" << std::endl;
        return status;
    } 

    /* Allocate memory for conversions in work() */
    size_t alignment = volk_get_alignment();

    _16icbuf_in = reinterpret_cast<int16_t *>(volk_malloc(2*buffer_size*sizeof(int16_t), alignment));
    _32fcbuf_in = reinterpret_cast<gr_complex *>(volk_malloc(buffer_size*sizeof(gr_complex), alignment));

    _16icbuf_out = reinterpret_cast<int16_t *>(volk_malloc(2*buffer_size*sizeof(int16_t), alignment));
    _32fcbuf_out = reinterpret_cast<gr_complex *>(volk_malloc(buffer_size*sizeof(gr_complex), alignment)); 

    _running = true; 
 
    return status;
}

void bladerfRadar_cc_impl::recv(){
    int status;
    //struct bladerf_metadata meta;
    //struct bladerf_metadata *meta_ptr = NULL;

    status = bladerf_sync_rx(dev, static_cast<void *>(_16icbuf_out),
            d_num_samples_send, NULL, timeout_ms*2);

    if (status != 0){
        std::cerr << "receiving failed: " << bladerf_strerror(status) << std::endl;
    } 
}

void bladerfRadar_cc_impl::send(){
    int status;

    status = bladerf_sync_tx(dev, static_cast<void const *>(_16icbuf_in), d_num_samples_send, NULL, timeout_ms*2); 

    if (status != 0){
        std::cerr << "sending failed: " << bladerf_strerror(status) << std::endl;
    } 
}

int bladerfRadar_cc_impl::work(int noutput_items,
                             gr_vector_const_void_star& input_items,
                             gr_vector_void_star& output_items)
{
    int status;

    if(d_new_freq){
        add_item_tag(0,nitems_written(0)+10,d_key,d_value_true,d_srcid);
        d_new_freq = false;
    }

    /**
     * process input_items
     *
     * */
    gr_complex const **in = reinterpret_cast<gr_complex const **>(&input_items[0]); 
    std::cout << _32fcbuf_in[0] << std::endl;

    memcpy(_32fcbuf_in, in[0], noutput_items * sizeof(gr_complex)); 

    // convert floating point to fixed point and scale
    // input_items is gr_complex (2x float), so num_points is 2*noutput_items
    volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
                            SCALING_FACTOR, 2*noutput_items);

    d_num_samples_send = noutput_items;
    //noutput_items = noutput_items*2;
    d_num_samples_recv = noutput_items;
    /**
     * create sending and receiving threads
     * */
    d_thread_send = gr::thread::thread(boost::bind(&bladerfRadar_cc_impl::send, this));
    d_thread_recv = gr::thread::thread(boost::bind(&bladerfRadar_cc_impl::recv, this)); 
    
    // Wait for threads to complete
    d_thread_send.join();
    d_thread_recv.join();
 

    // convert from int16_t to float
    // output_items is gr_complex (2x float), so num_points is 2*noutput_items
    volk_16i_s32f_convert_32f(reinterpret_cast<float *>(_32fcbuf_out), _16icbuf_out,
                            SCALING_FACTOR, 2*noutput_items);

    // copy the samples into output_items
    gr_complex **out = reinterpret_cast<gr_complex **>(&output_items[0]); 

    // we need to deinterleave the multiplex as we copy
    gr_complex const *deint_in = _32fcbuf_out;

    for (size_t i = 0; i < (noutput_items/2); ++i) {
        for (size_t n = 0; n < 2; ++n) {
            memcpy(out[n]++, deint_in++, sizeof(gr_complex));
        }
    }
    // no deinterleaving to do: simply copy everything
    //memcpy(out[0], _32fcbuf_out, sizeof(gr_complex) * noutput_items);

    /*num_samples_received = num_samples_received + noutput_items/2;
    if(num_samples_received >= d_tune_th){
        //std::cout << "received: " << num_samples_received << " samples" << std::endl;
        num_samples_received = 0;
        d_currrent_freq = d_currrent_freq + d_freq_step;
        //std::cout << "tune to next freq:" << d_currrent_freq << std::endl;
        if(d_currrent_freq > d_max_freq){
            std::cout << "reach max freq, tune back to :" << d_start_freq << std::endl;
            d_currrent_freq = d_start_freq;
        }

        status = bladerf_set_frequency(dev, BLADERF_CHANNEL_TX(0), d_currrent_freq);
        if (status != 0) {
            fprintf(stderr, "Failed to set frequency = %u: %s\n", BLADERF_CHANNEL_TX(0),
            bladerf_strerror(status));
        }

        status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(0), d_currrent_freq);
        if (status != 0) {
            fprintf(stderr, "Failed to set frequency = %u: %s\n", BLADERF_CHANNEL_RX(0),
            bladerf_strerror(status));
        }

        status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(1), d_currrent_freq);
        if (status != 0) {
            fprintf(stderr, "Failed to set frequency = %u: %s\n", BLADERF_CHANNEL_RX(1),
            bladerf_strerror(status));
        }
        add_item_tag(0,nitems_written(0),d_key,d_value_false,d_srcid);
        d_new_freq = true;
    }*/

    //auto in = static_cast<const input_type*>(input_items[0]);
    //auto out = static_cast<output_type*>(output_items[0]);

    // Do <+signal processing+>

    // Tell runtime system how many output items we produced.
    return noutput_items/2;
    //return noutput_items;
}

} /* namespace sfcwRadar */
} /* namespace gr */
