/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFRADAR_CC_IMPL_H
#define INCLUDED_SFCWRADAR_BLADERFRADAR_CC_IMPL_H

#include <gnuradio/sfcwRadar/bladerfRadar_cc.h>
#include <libbladeRF.h>

namespace gr {
namespace sfcwRadar {

struct channel_config {
    bladerf_channel channel;
    unsigned int frequency;
    unsigned int bandwidth;
    unsigned int samplerate;
    int gain;
};

class bladerfRadar_cc_impl : public bladerfRadar_cc
{
private:
    
    /**
     * bladerf device related 
     * */
    struct channel_config config;
    struct bladerf *dev = NULL;
    struct bladerf_devinfo dev_info;

    /**
     * Tags to split samples between two frequency steps
     * */
    pmt::pmt_t d_key, d_value_true, d_value_false, d_srcid;
    bool d_new_freq = true;

    // Sample-handling buffers
    int16_t *_16icbuf_in;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_in;           /**< intermediate buffer to gnuradio */ 
    
    int16_t *_16icbuf_out;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_out;           /**< intermediate buffer to gnuradio */


 /* These items configure the underlying asynch stream used by the sync
 * interface. The "buffer" here refers to those used internally by worker
 * threads, not the user's sample buffers.
 *
 * It is important to remember that TX buffers will not be submitted to
 * the hardware until `buffer_size` samples are provided via the
 * bladerf_sync_tx call. Similarly, samples will not be available to
 * RX via bladerf_sync_rx() until a block of `buffer_size` samples has been
 * received.
 */
    const unsigned int num_buffers = 8;
    const unsigned int buffer_size = 4096; /* Must be a multiple of 1024 */
    const unsigned int num_transfers = 4;
    const unsigned int timeout_ms = 3500;

    bool _running = false;

    int num_samples_received = 0;
    int d_tune_th;

    int d_num_samples_send;
    int d_num_samples_recv;

    int num_steps;
    bladerf_frequency d_start_freq;
    bladerf_frequency d_freq_step;
    bladerf_frequency d_currrent_freq;
    bladerf_frequency d_max_freq;

    /* Scaling factor used when converting from int16_t to float */
    const float SCALING_FACTOR = 2048.0f; 

    int configure_channel(struct bladerf *dev, struct channel_config *c);
    int init_sync(struct bladerf *dev); 
    void recv();
    void send(); 

public:
    bladerfRadar_cc_impl(bladerf_frequency start_freq,
                         int num_steps,
                         bladerf_frequency freq_step,
                         int samp_rate,
                         float rx_gain,
                         float tx_gain,
                         int tune_th);
    ~bladerfRadar_cc_impl();

    gr::thread::thread d_thread_send; 
    gr::thread::thread d_thread_recv;  

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFRADAR_CC_IMPL_H */
