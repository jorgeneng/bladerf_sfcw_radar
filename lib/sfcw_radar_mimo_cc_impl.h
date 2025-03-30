/* -*- c++ -*- */
/*
 * Author: Hui HUANG
 * Email: hui.huang@uni.lu
 *
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_SFCW_RADAR_MIMO_CC_IMPL_H
#define INCLUDED_SFCWRADAR_SFCW_RADAR_MIMO_CC_IMPL_H
/**
 * Use 2 TXs and 2 RXs
 * */
#define NUM_TX_CHANNELS 2
#define NUM_RX_CHANNELS 2

#define RADAR_TX BLADERF_CHANNEL_TX(0) /**TX 0 will be used for transmitting radar pulse*/
#define RADAR_RX BLADERF_CHANNEL_RX(0) /**RX 0 will be used for receiving radar echos*/
#define REF_TX BLADERF_CHANNEL_TX(1) /**TX 1 will be used for transmitting referece signal*/
#define REF_RX BLADERF_CHANNEL_RX(1) /**RX 1 will be used for receiving reference signal*/

#include <gnuradio/sfcwRadar/sfcw_radar_mimo_cc.h>
#include <libbladeRF.h>
#include <chrono>
#include "bladerf_device.h"

namespace gr {
namespace sfcwRadar {

class sfcw_radar_mimo_cc_impl : public sfcw_radar_mimo_cc
{
private:

protected:

    BladerfDevice *bladeRF; 
    const unsigned int timeout_ms = 2000;
    
    /**
     * single tone baseband signal
     * */
    float d_cw_amplitude;
    float d_cw_frequency;
    gr_complex d_phase = 0;
    
    /**
     * chirp waveform
     * */
    bool d_isChirp;
    float d_chirp_bandwidth;

    int d_samp_rate;
    int d_num_steps;
    /**
     * number of samples to transmit at each frequency step
     * */
    size_t d_burst_len; 
    /**
     * number of samples to receive at each frequency step
     * It is prefer to set d_recv_len > d_burst_len when using chirp pulse
     * */
    size_t d_recv_len;

    /**
     * FPGA time steps to wait for transmission after frequency tunning finished
     * */
    uint64_t d_ts_inc_send;

    /**
     * Change these flags upon reception of messages
     * d_scan = true && d_continuous_scan_flag = true. scan continousely
     * d_scan = true && d_continuous_scan_flag = false. scan only once
     * otherwise standby
     * */
    bool d_scan = false;
    bool d_continuous_scan_flag = false;

    /**
     * Preserved for store gps
     * */
    float d_gps_x = 0;
    float d_gps_y = 0;

    
    int16_t *_16icbuf_in;              /**< raw samples to bladeRF */
    gr_complex *_32fcbuf_in;           /**< buffer to store generated samples for transmission */ 
    
    int16_t *_16icbuf_out;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_out;           /**< buffer to store raw samples in 32 float*/

    /* Scaling factor used when converting from int16_t to float */
    const float SCALING_FACTOR = 2048.0f; 
    
    /**
     * set d_scan to true when a "scan" message is received
     * */
    void handle_scan_msg(const pmt::pmt_t& msg);
    
    void init_sample_buffers();
    
    /**
     * generate cw samples
     * */
    void generate_cw_samples();
    
    /**
     * generate chirp samples
     * */
    void generate_chirp_samples();

public:
    sfcw_radar_mimo_cc_impl(bladerf_frequency start_freq,
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
                            float ts_inc_send);
    ~sfcw_radar_mimo_cc_impl();
    
    /**
     * timer to record time consumption for A scan
     * */
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    int set_radar_tx_gain(bladerf_gain gain);
    int set_ref_tx_gain(bladerf_gain gain);
    int set_radar_rx_gain(bladerf_gain gain);
    int set_ref_rx_gain(bladerf_gain gain);

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_SFCW_RADAR_MIMO_CC_IMPL_H */
