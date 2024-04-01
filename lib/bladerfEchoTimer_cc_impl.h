/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFECHOTIMER_CC_IMPL_H
#define INCLUDED_SFCWRADAR_BLADERFECHOTIMER_CC_IMPL_H

#include <gnuradio/sfcwRadar/bladerfEchoTimer_cc.h>
#include <libbladeRF.h>
#include <chrono>

namespace gr {
namespace sfcwRadar {

struct channel_config {
    bladerf_channel channel;
    unsigned int frequency;
    unsigned int bandwidth;
    unsigned int samplerate;
    bladerf_gain gain;
};

class bladerfEchoTimer_cc_impl : public bladerfEchoTimer_cc
{
private:
    float d_amplitude;
    gr_complex d_phase;
    size_t d_burst_len;
    float d_frequency;
    
    /**
     * bladerf device related 
     * */
    struct channel_config config;
    struct bladerf *dev = NULL;
    struct bladerf_devinfo dev_info;
    
    size_t d_num_buffers;
    size_t d_buffer_size;
    size_t d_num_transfers;
    const unsigned int timeout_ms = 2000;
    int d_samp_rate;
    
    /**
     * Stepped frequency radar parameters
     * */
    int d_num_steps;
    bladerf_frequency d_start_freq;
    bladerf_frequency d_freq_step;
    bladerf_frequency d_currrent_freq;
    bladerf_frequency d_max_freq;
    int d_freq_index;
    struct bladerf_quick_tune *d_quick_tunes_tx;
    struct bladerf_quick_tune *d_quick_tunes_rx;
    
    // Sample-handling buffers
    int16_t *_16icbuf_in;              /**< raw samples to bladeRF */
    gr_complex *_32fcbuf_in;           /**< intermediate buffer from upstream block */ 
    
    int16_t *_16icbuf_out;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_out;           /**< intermediate buffer to downstream block*/

    /* Scaling factor used when converting from int16_t to float */
    const float SCALING_FACTOR = 2048.0f;
    
    int configure_channel(struct bladerf *dev, struct channel_config *c);
    int init_sync(struct bladerf *dev); 
    void recv();
    int wait_for_timestamp(struct bladerf *dev, bladerf_direction dir, uint64_t timestamp, unsigned int timeout_ms);
    void send(); 

    void set_tx_freq();
    void set_rx_freq();

    int set_quick_tune();

    int quick_tune(int index);

public:
    bladerfEchoTimer_cc_impl(bladerf_frequency start_freq,
                             int num_steps,
                             bladerf_frequency freq_step,
                             int samp_rate,
                             bladerf_gain rx_gain,
                             bladerf_gain tx_gain,
                             bladerf_gain ref_gain,
                             size_t burst_len,
                             size_t num_buffers,
                             size_t buffer_size,
                             size_t num_transfers);
    ~bladerfEchoTimer_cc_impl();
    
    gr::thread::thread d_thread_send; 
    gr::thread::thread d_thread_recv; 

    gr::thread::thread d_thread_setTxFreq;
    gr::thread::thread d_thread_setRxFreq;

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFECHOTIMER_CC_IMPL_H */
