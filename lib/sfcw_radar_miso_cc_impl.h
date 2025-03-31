/* -*- c++ -*- */
/*
 * Copyright 2025 snt.
 * Author: Hui HUANG
 * Email: hui.huang@uni.lu
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_SFCW_RADAR_MISO_CC_IMPL_H
#define INCLUDED_SFCWRADAR_SFCW_RADAR_MISO_CC_IMPL_H
/**
 * Use 1 TXs and 2 RXs
 * */
#define NUM_TX_CHANNELS 1
#define NUM_RX_CHANNELS 2

#define RADAR_TX BLADERF_CHANNEL_TX(0) /**TX 0 will be used for transmitting radar pulse*/
#define RADAR_RX BLADERF_CHANNEL_RX(0) /**RX 0 will be used for receiving radar echos*/
#define REF_RX BLADERF_CHANNEL_RX(1) /**RX 1 will be used for receiving reference signal*/

#include <gnuradio/sfcwRadar/sfcw_radar_miso_cc.h>
#include <libbladeRF.h>
#include <chrono>
#include "bladerf_device.h"

namespace gr {
namespace sfcwRadar {

/**
 * This class implement a SFCW radar.
 * This version uses only one TX channel for transmitting radar pulse. 
 * A directional coupler connected to the TX port feed the copy of the transmitting pulse to the reference RX port
 * See macro for channel definitions.
 * Two waveforms, single tone or chirp, are supported
 * */
class sfcw_radar_miso_cc_impl : public sfcw_radar_miso_cc
{
private:
    
    /**
     * Pointer to the BladerfDevice instance
     * */
    BladerfDevice *bladeRF; 
    const unsigned int timeout_ms = 2000;
    
    /**
     * Amplitude of pulse
     * */
    float d_pulse_amplitude;
    
    /**
     * single tone baseband signal
     * */
    float d_cw_frequency;
    gr_complex d_phase = 0;
    
    /**
     * chirp waveform
     * */
    bool d_isChirp;
    float d_chirp_bandwidth;

    /**
     * Sampling rate
     * */
    int d_samp_rate;

    /**
     * number of frequency steps
     * */
    int d_num_steps;

    /**
     * number of samples in a pulse to be transmitted at each frequency step
     * */
    size_t d_burst_len; 

    /**
     * number of samples to receive from *one RX channel* at each frequency step
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
     * timer to record time consumption for A scan
     * */
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    
    /**
     * set d_scan to true when a "scan" message is received
     * */
    void handle_scan_msg(const pmt::pmt_t& msg);
    
    /**
     * Initialise _16icbuf_in, _32fcbuf_in, _16icbuf_out, _32fcbuf_out
     * The size of _16icbuf_in: 2 * NUM_TX_CHANNELS * d_burst_len * sizeof(int16_t)
     * The size of _16icbuf_out: 2 * NUM_TX_CHANNELS * d_burst_len * sizeof(int16_t)
     * The size of _32fcbuf_in: NUM_TX_CHANNELS * d_burst_len * sizeof(gr_complex)
     * The size of _32fcbuf_out: NUM_TX_CHANNELS * d_burst_len * sizeof(gr_complex)
     * */
    void init_sample_buffers();
    
    /**
     * Generate single tone samples, and store them to _32fcbuf_in
     * The samples to be transmitted via the two TX channels are interleaved
     * */
    void generate_cw_samples();
    
    /**
     * Generate chirp samples, and store them to _32fcbuf_in
     * The chirp is defined by d_chirp_bandwidth, d_burst_len and d_samp_rate 
     * The amplitude is defined by d_pulse_amplitude
     * The samples to be transmitted via the two TX channels are interleaved
     * */
    void generate_chirp_samples();

public:
    
    /**
     * Class Constructor.
     * The jobs include:
     * 1. Initialise sample buffers @see init_sample_buffers()
     * 2. Create an instance of BladerfDevice, and set it to use on TX and two RXs
     * 3. Provide frequency plan to the device to enable quick tune functionality
     * @param   start_freq  The start frequency of the frequency plan
     * @param   num_steps   Number of frequency steps
     * @param   step_size   The interval between two consecutive frequencies
     * @param   samp_rate   Sampling rate
     * @param   rx_gain     The gain of the radar RX channel
     * @param   tx_gain     The gain of the radar TX channel
     * @param   ref_gain    The gain of the reference TX and RX channel
     * @param   enable_biastee  Set the flag if BT-100 and BT-200 are connected with radar TX and radar RX channels
     * @param   burst_len   Number of samples per pulse
     * @param   recv_buf_len    Number of samples to receive from one RX channel. Prefer to be bigger than burst_len
     * @param   num_buffers     Number of buffers to use in the underlying data stream
     * @param   buffer_size     The size of the underlying steam buffers, in samples. Must be a multiple of 1024. Samples are only transferred when a buffer of this size is filled.
     * @param   num_transfers   The number of active USB transfers that may be in-flight at any given time
     * @param   pulse_amplitude    The amplitude of the transmitted pulse
     * @param   cw_frequency    The baseband frequency of the single tone pulse
     * @param   isChirp     Set this when using chirp waveform
     * @param   chirp_bandwidth     Bandiwdth of chirp
     * @param   ts_inc_send     After each frequency tunning, wait ts_inc_send ms before transmitting radar pulse and receiving radar echo. Note that the value depends on the processing power and the USB overhead of the host computer. It is recommand to be larger than 1.
     * */
    sfcw_radar_miso_cc_impl(bladerf_frequency start_freq,
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
                            float pulse_amplitude,
                            float cw_frequency,
                            bool isChirp,
                            float chirp_bandwidth,
                            float ts_inc_send);
    ~sfcw_radar_miso_cc_impl();
    
    /**
     * Set gain for radar TX channel
     * @param   gain    The expected gain
     * @return 0 if success
     * */
    int set_radar_tx_gain(bladerf_gain gain);
    
    /**
     * Set gain for radar RX channel
     * @param   gain    The expected gain
     * @return 0 if success
     * */
    int set_radar_rx_gain(bladerf_gain gain);
    
    /**
     * Set gain for reference RX channel
     * @param   gain    The expected gain
     * @return 0 if success
     * */
    int set_ref_rx_gain(bladerf_gain gain);


    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_SFCW_RADAR_MISO_CC_IMPL_H */
