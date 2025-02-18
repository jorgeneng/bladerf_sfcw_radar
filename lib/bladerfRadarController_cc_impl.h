/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFRADARCONTROLLER_CC_IMPL_H
#define INCLUDED_SFCWRADAR_BLADERFRADARCONTROLLER_CC_IMPL_H

#include <gnuradio/sfcwRadar/bladerfRadarController_cc.h>
#include <libbladeRF.h>
#include <chrono>

#define RADAR_TX BLADERF_CHANNEL_TX(0)
#define RADAR_RX BLADERF_CHANNEL_RX(1)
#define REF_TX BLADERF_CHANNEL_TX(1)
#define REF_RX BLADERF_CHANNEL_RX(0)

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

class bladerfRadarController_cc_impl : public bladerfRadarController_cc
{
private:
    /**
     * bladerf device related 
     * */
    struct channel_config config;
    struct bladerf *dev = NULL;
    struct bladerf_devinfo dev_info;
    
    /**
     * bladerf tx/rx buffer setup
     * */
    size_t d_num_buffers;
    size_t d_buffer_size;
    size_t d_num_transfers;
    const unsigned int timeout_ms = 4000;

    /**
     * number of samples to transmit at each frequency step
     * */
    size_t d_burst_len; 
    /**
     * number of samples to receive at each frequency step
     * It is prefer to set d_recv_len > d_burst_len when using chirp pulse
     * */
    size_t d_recv_len; 
    int d_num_steps; // number of frequency steps
    int d_samp_rate;
    unsigned int d_channel_bandwidth;
    bladerf_gain d_rx_gain;
    bladerf_gain d_tx_gain;
    bladerf_gain d_ref_gain;
    bool d_enable_biastee;
    bladerf_frequency d_start_freq; //the radar starts from this frequency
    bladerf_frequency d_step_size;  //the bandwidth of each frequency step
    int d_freq_index;
    
    /**
     * FPGA time steps to wait for transmission after frequency tunning finished
     * */
    uint64_t d_ts_inc_rec;
    /**
     * keep this 0
     * */
    uint64_t d_ts_inc_send;

    /**
     * Tx and Rx metadata
     * */
    struct bladerf_metadata d_rx_meta;
    struct bladerf_metadata d_tx_meta;

    float d_cw_amplitude;
    float d_cw_frequency;
    gr_complex d_phase = 0;
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
    /**
     * Preserved for store current gps
     * */
    float d_gps_x = 0;
    float d_gps_y = 0;

    
    int16_t *_16icbuf_in;              /**< raw samples to bladeRF */
    gr_complex *_32fcbuf_in;           /**< intermediate buffer from upstream block */ 
    
    int16_t *_16icbuf_out;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_out;           /**< intermediate buffer to downstream block*/

    /* Scaling factor used when converting from int16_t to float */
    const float SCALING_FACTOR = 2048.0f; 
    
    int init_device();
    
    /**
     * 1. Configure both the device's X2 RX and X2 TX channels for use with the
     * synchronous interface. SC16 Q11 samples *with* metadata are used.
     * TX0 and RX0 are used for transmitting and receiving radar echos
     * TX1 and RX1 are used for transmitting and receiving ref signals
     * 2. Enable BLADERF_CHANNEL_RX(0), BLADERF_CHANNEL_RX(1), BLADERF_CHANNEL_TX(0) and BLADERF_CHANNEL_TX(1) 
     * 3. Read gains of the above three channel to confirm if gain setup was success
     * */
    int init_sync(struct bladerf *dev);
    
    /**
     * Setup given channel
     * 1. LO frequency 
     * 2. Sample rate
     * 3. gain
     *
     * return 0 if everything is OK
     * */
    int configure_channel(struct bladerf *dev, struct channel_config *c);
    
    /**
     * Get quick tune parameters for each frequency we'll be using
     * */
    int set_quick_tune();
    
    /**
     * re-tune LO frequency of TX and two RXs to the frequency indicated by index
     * */
    int quick_tune();

    void tune_rx();
    void tune_tx();
    
    /**
     * set d_scan to true when a "scan" message is received
     * */
    void handle_scan_msg(const pmt::pmt_t& msg);
    
    /**
     * generate cw samples
     * */
    void generate_cw_samples();

    /**
     * generate chirp samples
     * */
    bool d_isChirp = false;
    float d_chirp_bandwidth = 5e6;
    void generate_chirp_samples();
    
    void send();
    void recv();
    
    int wait_for_timestamp(struct bladerf *dev, bladerf_direction dir, uint64_t timestamp, unsigned int timeout_ms);


public:
    bladerfRadarController_cc_impl(bladerf_frequency start_freq,
                                   int num_steps,
                                   bladerf_frequency step_size,
                                   int samp_rate,
                                   bladerf_gain rx_gain,
                                   bladerf_gain tx_gain,
                                   bladerf_gain ref_gain,
                                   bool enable_biastee,
                                   size_t burst_len,
                                   size_t recv_buf_len,
                                   size_t num_buffers,
                                   size_t buffer_size,
                                   size_t num_transfers,
                                   float cw_amplitude,
                                   float cw_frequency,
                                   bool isChirp,
                                   float chirp_bandwidth,
                                   float ts_inc_send,
                                   float ts_inc_recv);
    ~bladerfRadarController_cc_impl();

    int set_tx_gain(bladerf_gain tx_gain);
    int set_rx_gain(bladerf_gain rx_gain);
    int set_ref_gain(bladerf_gain ref_gain);
    int set_chirp_bandwidth(float chirp_bandwidth);
    /**
     * thread handles for receive and send thread
     * */
    gr::thread::thread d_thread_send; 
    gr::thread::thread d_thread_recv; 
    
    /**
     * thread handles for tx and rx tuning 
     * */
    gr::thread::thread d_thread_rx_freq_tuning; 
    gr::thread::thread d_thread_tx_freq_tuning; 
    
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFRADARCONTROLLER_CC_IMPL_H */
