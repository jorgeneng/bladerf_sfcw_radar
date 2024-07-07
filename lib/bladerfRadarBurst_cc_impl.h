/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFRADARBURST_CC_IMPL_H
#define INCLUDED_SFCWRADAR_BLADERFRADARBURST_CC_IMPL_H

#include <gnuradio/sfcwRadar/bladerfRadarBurst_cc.h>
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

struct bladerf_quick_tune_info{
    bladerf_frequency freq;
    bladerf_quick_tune quick_tune;
};

class bladerfRadarBurst_cc_impl : public bladerfRadarBurst_cc
{
private:
    /**
     * bladerf device related 
     * */
    struct channel_config config;
    struct bladerf *dev = NULL;
    struct bladerf_devinfo dev_info;
    
    /**
     * bladerf buffer setup
     * */
    size_t d_num_buffers;
    size_t d_buffer_size;
    size_t d_num_transfers;
    const unsigned int timeout_ms = 2000;

    /**
     * Stepped frequency radar parameters
     * */
    size_t d_burst_len;
    int d_num_steps; // number of frequency steps
    int d_samp_rate;
    bladerf_gain d_rx_gain;
    bladerf_gain d_tx_gain;
    bladerf_gain d_ref_gain;
    bladerf_frequency d_start_freq; //the radar starts from this frequency
    bladerf_frequency d_freq_step;  //the bandwidth of each frequency step
    bladerf_frequency d_currrent_freq;  //current frequency of the radar
    bladerf_frequency d_max_freq; //the radar goes back to d_start_freq until it reaches here
    int d_freq_index;
    //struct bladerf_quick_tune *d_quick_tunes_tx;
    struct bladerf_quick_tune_info *d_quick_tunes_tx;
    //struct bladerf_quick_tune *d_quick_tunes_rx;
    struct bladerf_quick_tune_info *d_quick_tunes_rx;

    /**
     * Change these flags upon reception of messages
     * d_scan = true && d_continuous_scan_flag = true. scan continousely
     * d_scan = true && d_continuous_scan_flag = false. scan only once
     * otherwise standby
     * */
    bool d_scan = false;
    bool d_continuous_scan_flag = false;
    float d_gps_x = 0;
    float d_gps_y = 0;

    // Sample-handling buffers
    unsigned int d_num_samples_to_send;
    unsigned int d_num_samples_to_recv;
    
    int16_t *_16icbuf_in;              /**< raw samples to bladeRF */
    gr_complex *_32fcbuf_in;           /**< intermediate buffer from upstream block */ 
    
    int16_t *_16icbuf_out;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_out;           /**< intermediate buffer to downstream block*/

    gr_complex *d_cw_buf;

    /* Scaling factor used when converting from int16_t to float */
    const float SCALING_FACTOR = 2048.0f; 

    int init_device();
    
    /**
     * Setup given channel
     * 1. LO frequency 
     * 2. Sample rate
     * 3. gain
     * 4. Disable AGC 
     *
     * return 0 if everything is OK
     * */
    int configure_channel(struct bladerf *dev, struct channel_config *c);

    /**
     * 1. Configure both the device's X2 RX and X1 TX channels for use with the
     * synchronous interface. SC16 Q11 samples *without* metadata are used.
     * Use BLADERF_FORMAT_SC16_Q11 instead of BLADERF_FORMAT_SC16_Q11_META cause the META mode does not work with two RXs due to FPGA bug
     * 2. Enable BLADERF_CHANNEL_RX(0), BLADERF_CHANNEL_RX(1) and BLADERF_CHANNEL_TX(0)
     * 3. Read gains of the above three channel to confirm if gain setup was success
     * 4. Initialize _16icbuf_in, _32fcbuf_in, _16icbuf_out and _32fcbuf_out buffers
     * */
    int init_sync(struct bladerf *dev);

    /**
     * Get quick tune parameters for each frequency we'll be using
     * */
    int set_quick_tune();

    /**
     * re-tune LO frequency of TX and two RXs to the frequency indicated by index
     * */
    int quick_tune(int index);

    /**
     * receive thread
     * */
    void recv();

    /**
     * Do not use this function
     * */
    int wait_for_timestamp(struct bladerf *dev, bladerf_direction dir, uint64_t timestamp, unsigned int timeout_ms);
    
    /**
     * send thread
     * */
    void send(); 

    /**
     * set d_scan to true when a "scan" message is received
     * */
    void handle_scan_msg(const pmt::pmt_t& msg);

    /**
     * generate cw samples
     * */
    void generate_cw_samples();

protected:
    int calculate_output_stream_length(const gr_vector_int& ninput_items);

public:
    bladerfRadarBurst_cc_impl(bladerf_frequency start_freq,
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
    ~bladerfRadarBurst_cc_impl();
    
    /**
     * thread handles for receive and send thread
     * */
    gr::thread::thread d_thread_send; 
    gr::thread::thread d_thread_recv; 

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    /**
     * callback functions for setting gains of the TX and two RX channels
     * */
    int set_rx_gain(bladerf_gain gain);
    int set_ref_gain(bladerf_gain gain);
    int set_tx_gain(bladerf_gain gain);

    /**
     * callback functions for setting radar frequencies
     * */
    int set_start_freq(bladerf_frequency start_freq);
    int set_freq_step(bladerf_frequency freq_step);
    int set_num_steps(int num_steps);
    int set_burst_len(int burst_len);

    void update_gps();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_int& ninput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFRADARBURST_CC_IMPL_H */
