/* -*- c++ -*- */
/*
 * Author: Hui HUANG
 * Email: hui.huang@uni.lu
 * Date: 04/2025
 *
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "bladerf_device.h"
#include <iostream>
#include <cstring>
#include <thread>

BladerfDevice::BladerfDevice() : device(nullptr) {
    /**
     * Initialize tx and rx metadata
     * */
    memset(&d_rx_meta, 0, sizeof(d_rx_meta));
    memset(&d_tx_meta, 0, sizeof(d_tx_meta));
    d_tx_meta.flags = BLADERF_META_FLAG_TX_BURST_START | BLADERF_META_FLAG_TX_BURST_END; /**< send as burst_len*/

    // Initialize atomic counters to zero
    m_send_failures = 0;
    m_recv_failures = 0;
    m_tune_events = 0;

    // Open the log file for writing, overwriting any previous content
    m_log_file.open(m_log_filename, std::ios::out | std::ios::trunc);
    if (m_log_file.is_open()) {
        m_log_file << "send_failures,recv_failures,tune_events, error_rate" << std::endl;
        //write_stats_to_file(); // Write initial zero values
    } else {
        std::cerr << "ERROR: Could not open log file: " << m_log_filename << std::endl;
    } 
}

BladerfDevice::~BladerfDevice() {
    closeDevice(); 
    // Close the log file when the object is destroyed
    if (m_log_file.is_open()) {
        m_log_file.close();
    } 
}

// Helper function to write stats (add this new function)
void BladerfDevice::write_stats_to_file() {
    if (m_log_file.is_open()) {
        // Seek to the beginning of the file to overwrite, or append
        m_log_file.seekp(0); // Overwrite the file with the latest stats
        m_log_file << "send_failures: " << m_send_failures << std::endl;
        m_log_file << "past timestamp failures: " << m_recv_failures << std::endl;
        m_log_file << "Overrun errors: " << m_recv_overrun << std::endl;
        m_log_file << "number_tuning: " << m_tune_events << std::endl;
        m_log_file << "past_timestamp_error_rate: " << (m_recv_failures)/(float)m_tune_events << std::endl;
        m_log_file << "overrun_error_rate: " << (m_recv_overrun)/(float)m_tune_events << std::endl;
        m_log_file << "tuning_time: " << d_tuning_time/m_tune_events << std::endl;
        m_log_file << "pulse_time: " << d_tuning_time/m_tune_events << std::endl;
        
        std::cout << d_tuning_time << std::endl;
        std::cout << d_pulse_time << std::endl;
        std::cout << m_tune_events << std::endl;
        m_log_file.flush(); // Ensure data is written immediately
    }
}

bool BladerfDevice::openDevice() {
    std::cout << "*************************Open device************************" <<std::endl;
    bladerf_init_devinfo(&dev_info);
    std::cout << "dev_info" << &dev_info <<  std::endl;
    int status = bladerf_open_with_devinfo(&device, &dev_info);

    if (status!= 0) {
        std::cerr << "Error opening BladeRF device: " << bladerf_strerror(status) << std::endl;
        device = nullptr;
        return false;
    }

    char serial[BLADERF_SERIAL_LENGTH];
    if (bladerf_get_serial(device, serial)==0){
        std::string strser(serial);
        std::cout << " Serial # " << strser << std::endl;
    }else{
        std::cerr << "Failed to get device serial number" << std::endl;
        return false;
    }
    if (bladerf_is_fpga_configured(device)==1){
        std::cout << "FPGA is already loaded" << std::endl;
    }else{
        std::cerr << "FPGA not loaded" << std::endl;
        return false;
    }
    /**
    * set tunning mode to FPGA to get fast frequency tunning
    * */
    bladerf_set_tuning_mode(device, BLADERF_TUNING_MODE_FPGA);
    bladerf_tuning_mode current_mode;
    bladerf_get_tuning_mode(device, &current_mode);
    std::cout << "Tunning mode is: " << current_mode << std::endl;
    std::cout << "BladeRF device opened successfully!" << std::endl;
    return true;
}

void BladerfDevice::closeDevice() {
    if (device != nullptr) {
        bladerf_close(device);
        std::cout << "BladeRF device closed." << std::endl;
        device = nullptr;
    }
}

int BladerfDevice::configure_channel(struct channel_config *c){
    if(device == nullptr){
        std::cerr<<"configure_channel: Device is not available, open device first" << std::endl;
        return -1;
    }
    int status;
    /**
     * Set LO frequency
     * */
    status = bladerf_set_frequency(device, c->channel, c->frequency);
    if (status != 0) {
        fprintf(stderr, "Failed to set frequency = %u: %s\n", c->frequency,
        bladerf_strerror(status));
        return status;
    }
    bladerf_frequency current_freq;
    status = bladerf_get_frequency(device, c->channel, &current_freq);
    if(status!=0){
        std::cerr<<"Failed to read frequency from Channel: " << c->channel << std::endl;
    }else{
        std::cout << "Set chennel" << c->channel << ", frequency: " << current_freq << std::endl;
    }

    /**
     * Set sampling rate
     * */
    unsigned int actual_value;
    status = bladerf_set_sample_rate(device, c->channel, c->samplerate, &actual_value);
    if (status != 0) {
        fprintf(stderr, "Failed to set samplerate = %u: %s\n", c->samplerate,
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "Set chennel" << c->channel << ", samplerate: " << actual_value << std::endl;
    }

    /**
     * Set gain
     * */
    std::cout << "Set channel " << c->channel << " gain to "<< c->gain << std::endl;
    status = bladerf_set_gain(device, c->channel, c->gain);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain: %s\n", bladerf_strerror(status));
        return status;
    }

    return status; 
}

int BladerfDevice::enable_rx_channels(struct channel_config *ref_rx_config, struct channel_config *radar_rx_config, struct usb_buffer_config *buf_config, bool enable_biastee){
    
    if(device==nullptr){
        std::cerr<<"enable rx channels: Device is not available, open device first" << std::endl;
        return -1;
    }
    
    int status;
    bladerf_channel_layout rx_channel_layout;

    if(ref_rx_config==nullptr){
        std::cout << "ref_rx_config is nullptr, only setup radar RX channel " << std::endl;
        rx_channel_layout = BLADERF_RX_X1;
    }else{
        std::cout << "Will setup two RX channels, one for radar RX, one for reference RX" << std::endl;
        rx_channel_layout = BLADERF_RX_X2;
        status = configure_channel(ref_rx_config);
        if (status !=0){
            std::cerr << "Channel " << ref_rx_config->channel << ": configure_channel failed" << std::endl;
            return status;
        }else{
            std::cout << "Channel " << ref_rx_config->channel << ": configure_channel succed" << std::endl;
        }
        /**
        * Set AGC for REF_RX
        * */
        status = bladerf_set_gain_mode(device, ref_rx_config->channel, ref_rx_config->gain_mode);
        if (status != 0) {
            fprintf(stderr, "Failed to set gain mode = %u: %s\n", ref_rx_config->channel,
            bladerf_strerror(status));
            return status;
        }else{
            std::cout << "Channel: " << ref_rx_config->channel << ", gain mode: " << ref_rx_config->gain_mode << std::endl;
        }
    }
    
    /**
     * Configure radar RX Channel
     * */
    status = configure_channel(radar_rx_config);
    if (status !=0){
        std::cerr << "Channel " << radar_rx_config->channel << ": configure_channel failed" << std::endl;
        return status;
    }else{
        std::cout << "Channel " << radar_rx_config->channel << ": configure_channel succed" << std::endl;
    }
    
    /**
     * Set bias tee of radar_rx_channel
     * */
    status = bladerf_set_bias_tee(device, radar_rx_config->channel, enable_biastee);
    if(status != 0){
        std::cerr << "Set channel: " << radar_rx_config->channel << " bias tee failed" << std::endl;
        return status;
    }else{
        bool is_bias_tee_enabled = false;
        status = bladerf_get_bias_tee(device,radar_rx_config->channel, &is_bias_tee_enabled);
        std::cout << "bias tee status of chennel " << radar_rx_config->channel << " :" << is_bias_tee_enabled << std::endl;
    }
    
    /**
     * Set AGC of radar_rx_channel
     * */
    status = bladerf_set_gain_mode(device, radar_rx_config->channel, radar_rx_config->gain_mode);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode = %u: %s\n", radar_rx_config->channel,
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "Channel: " << radar_rx_config->channel << ", gain mode: " << radar_rx_config->gain_mode << std::endl;
    }
    
    /* Configure the device's RX channels for use with the
    * synchronous
    * interface. SC16 Q11 samples *with* metadata are used. */
 
    status = bladerf_sync_config(device, rx_channel_layout, 
                                 BLADERF_FORMAT_SC16_Q11_META, buf_config->num_buffers, 
                                 buf_config->buffer_size, buf_config->num_transfers,timeout_ms);

    if (status != 0) {
        fprintf(stderr, "Failed to configure RX sync interface: %s\n",
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "RX sync interface configured. num_buffers:  "<< buf_config->num_buffers 
            << ", buffer_size: " << buf_config->buffer_size 
            << ", num_transfers: " << buf_config->num_transfers 
            << ", timeout_ms: " << timeout_ms << std::endl;
    }
    
    /**
     * Enable rx channels
     * */
    status = bladerf_enable_module(device, radar_rx_config->channel, true);
    if (status != 0) {
        std::cerr << "RADAR_RX enable failed" << std::endl;
        return status;
    }else{
        std::cout << "RADAR_RX enalbed" << std::endl;
    }

    if(rx_channel_layout == BLADERF_RX_X2){
        status = bladerf_enable_module(device, ref_rx_config->channel, true);
        if (status != 0) {
            std::cerr << "REF_RX enable failed" << std::endl;
            return status;
        }else{
            std::cout << "REF_RX enalbed" << std::endl;
        }
    }
    return status;
}


int BladerfDevice::enable_tx_channels(struct channel_config *ref_tx_config, struct channel_config *radar_tx_config, struct usb_buffer_config *buf_config, bool enable_biastee){
    if(device==nullptr){
        std::cerr<<"enable_tx_channels: Device is not available, open device first" << std::endl;
        return -1;
    }

    int status;
    bladerf_channel_layout tx_channel_layout;

    if(ref_tx_config == nullptr){
        std::cout << "ref_tx_config is nullptr, only set up radar TX channel" << std::endl;
        tx_channel_layout = BLADERF_TX_X1;
    }else{
        std::cout << "Will setup two TX channels, one for radar TX, one for reference TX" << std::endl;
        tx_channel_layout = BLADERF_TX_X2;
        status = configure_channel(ref_tx_config);
        if (status !=0){
            std::cerr << "Channel " << ref_tx_config->channel << ": configure_channel failed" << std::endl;
            return status;
        }else{
            std::cout << "Channel " << ref_tx_config->channel << ": configure_channel succed" << std::endl;
        }
    }

    /**
     * Configure radar TX channel
     * */
    status = configure_channel(radar_tx_config);
    if (status !=0){
        std::cerr << "Channel " << radar_tx_config->channel << ": configure_channel failed" << std::endl;
        return status;
    }else{
        std::cout << "Channel " << radar_tx_config->channel << ": configure_channel succed" << std::endl;
    }
    
    /**
     * Set bias tee for RADAR_TX
     * */
    status = bladerf_set_bias_tee(device, radar_tx_config->channel, enable_biastee);
    if(status != 0){
        std::cerr << "Set channel: " << radar_tx_config->channel << " bias tee failed" << std::endl;
        return status;
    }else{
        bool is_bias_tee_enabled = false;
        status = bladerf_get_bias_tee(device, radar_tx_config->channel, &is_bias_tee_enabled);
        std::cout << "bias tee status of chennel " << radar_tx_config->channel << " :" << is_bias_tee_enabled << std::endl;
    }
    
    /* Configure both the device's TX channels for use with the
    * synchronous
    * interface. SC16 Q11 samples *with* metadata are used. */
 
    status = bladerf_sync_config(device, tx_channel_layout, 
                                 BLADERF_FORMAT_SC16_Q11_META, buf_config->num_buffers, 
                                 buf_config->buffer_size, buf_config->num_transfers,timeout_ms);

    if (status != 0) {
        fprintf(stderr, "Failed to configure TX sync interface: %s\n",
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "TX sync interface configured. num_buffers:  "<< buf_config->num_buffers 
            << ", buffer_size: " << buf_config->buffer_size 
            << ", num_transfers: " << buf_config->num_transfers 
            << ", timeout_ms: " << timeout_ms << std::endl;
    }

    /**
     * Enable the TX channels
     * */
    status = bladerf_enable_module(device, radar_tx_config->channel, true);
    if (status != 0) {
        std::cerr << "RADAR_TX enable failed" << std::endl;
        return status;
    }else{
        std::cout << "RADAR_TX enalbed" << std::endl;
    } 

    if(tx_channel_layout == BLADERF_TX_X2){
        status = bladerf_enable_module(device, ref_tx_config->channel, true);
        if (status != 0) {
            std::cerr << "REF_TX enable failed" << std::endl;
            return status;
        }else{
            std::cout << "REF_TX enalbed" << std::endl;
        }
    }

    return status;
}

int BladerfDevice::enable_channels(struct channel_config *radar_tx_config, struct channel_config *radar_rx_config, 
        struct channel_config *ref_tx_config, struct channel_config *ref_rx_config,
        struct usb_buffer_config *buf_config, bool enable_biastee){
    
    if(device==nullptr){
        std::cerr<<"enable_channels: Device is not available, open device first" << std::endl;
        return -1;
    }

    if(radar_tx_config==nullptr||radar_rx_config==nullptr){
        std::cerr << "Provide at least channel configurations for radar TX and radar RX channels" << std::endl;
        return -1;
    }

    int status;
    status = enable_rx_channels(ref_rx_config, radar_rx_config, buf_config, enable_biastee);
    if(status!=0){
        closeDevice();
        device = nullptr;
        return status;
    }

    status = enable_tx_channels(ref_tx_config, radar_tx_config, buf_config, enable_biastee);
    if(status!=0){
        closeDevice();
        device = nullptr;
        return status;
    }
    
    std::cout << "TX and RX channels enabled" << std::endl;
    return status;
}

int BladerfDevice::set_quick_tune(struct frequency_plan_config *frequency_plan){
    int status;
    d_quick_tunes_tx = new bladerf_quick_tune_info[frequency_plan->num_steps];
    d_quick_tunes_rx = new bladerf_quick_tune_info[frequency_plan->num_steps]; 
    bladerf_frequency freq = frequency_plan->start_freq;
    for (int i = 0; i < frequency_plan->num_steps; i++){
        //std::cout << "set quick tune parameters for frequency: " << freq << std::endl;
        status = bladerf_set_frequency(device, BLADERF_TX, freq);
        if(status!=0){
            std::cerr << "set TX frequency to: "<< freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_tx[i].freq = freq;
        status = bladerf_get_quick_tune(device, BLADERF_TX, &d_quick_tunes_tx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for TX" << std::endl;
            return status;
        }
        
        status = bladerf_set_frequency(device, BLADERF_RX, freq);
        if(status!=0){
            std::cerr << "set RX frequency to: "<< freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_rx[i].freq = freq;
        status = bladerf_get_quick_tune(device, BLADERF_RX, &d_quick_tunes_rx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for RX" << std::endl;
            return status;
        }
        freq = freq + frequency_plan->step_size;
    }

    //save frequency plan for future use
    d_start_freq = frequency_plan->start_freq;
    d_num_steps = frequency_plan->num_steps;
    d_step_size = frequency_plan->step_size;
    return status;
}

int BladerfDevice::tune_rx(int freq_index){
    if(freq_index>=d_num_steps){
        std::cerr << "the input freq_index: "<< freq_index << " is out of range" <<std::endl;
        return -1;
    }
    int status = bladerf_schedule_retune(device, BLADERF_RX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_rx[freq_index].quick_tune);
    if(status != 0){
        std::cerr << "failed to tune RX: " << bladerf_strerror(status) << std::endl;
    }
    return status;
}


int BladerfDevice::tune_tx(int freq_index){
    if(freq_index>=d_num_steps){
        std::cerr << "the input freq_index: "<< freq_index << " is out of range" <<std::endl;
        return -1;
    }

    m_tune_events++; // Increment the tune counter
    
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    int status = bladerf_schedule_retune(device, BLADERF_TX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_tx[freq_index].quick_tune);
    if(status != 0){
        std::cerr << "failed to tune RX: " << bladerf_strerror(status) << std::endl;
    }
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    d_tuning_time = d_tuning_time + std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count();
    return status;
}

/**
 * send the samples stored in _16icbuf_in
 * sending through tow tx ports, the number of samples to send equals to the burst_len x 2
 * */
void BladerfDevice::send(){
    int status;
    status = bladerf_sync_tx(device, static_cast<void const *>(_16icbuf_in), _16icbuf_in_num_samples, &d_tx_meta, timeout_ms); 

    if (status != 0){
        std::cerr << "sending failed: " << bladerf_strerror(status) << std::endl;
        m_send_failures++; // Increment on failure
    }
}

/**
 * receive samples from two RXs, and store the received samples in _16icbuf_out
 * we are expecting to receive d_num_samples_to_recv samples, the size is twice of the busrt_len
 * as the samples from two RXs are interleaved
 * */
void BladerfDevice::recv(){
    int status;
    status = bladerf_sync_rx(device, static_cast<void *>(_16icbuf_out), _16icbuf_out_num_samples, &d_rx_meta, timeout_ms);

    if (status != 0){
        std::cerr << "receiving failed: " << bladerf_strerror(status) << std::endl;
        m_recv_failures++; // Increment on failure
    }else if (d_rx_meta.status & BLADERF_META_STATUS_OVERRUN){
        std::cerr << "Overrun detected in scheduled RX. Number of samples read is: " << d_rx_meta.actual_count << std::endl;
        m_recv_overrun++; // Increment on failure
    }
}

int BladerfDevice::pulse(float d_ts_inc_send, float d_ts_inc_recv, int16_t *samples_to_send, unsigned int num_samples_to_send, int16_t *rec_buf, unsigned int num_samples_to_recv){
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    /**
     * Setup sending and receiving buf, guys who call this function are responsible for preparing buffers and samples.
     * */
    _16icbuf_in = samples_to_send;
    _16icbuf_in_num_samples = num_samples_to_send;
    _16icbuf_out = rec_buf;
    _16icbuf_out_num_samples = num_samples_to_recv;
    
    /**
     * Make sure the flags of tx and rx are correct
     * */
    d_tx_meta.flags = BLADERF_META_FLAG_TX_BURST_START | BLADERF_META_FLAG_TX_BURST_END;// | BLADERF_META_FLAG_TX_NOW;// | BLADERF_META_FLAG_TX_UPDATE_TIMESTAMP;
    d_rx_meta.flags = 0;//BLADERF_META_FLAG_RX_NOW;

    /**
     * Get current FPGA time stamp of the device.
     * */
    int status = bladerf_get_timestamp(device, BLADERF_RX, &d_rx_meta.timestamp);
    if (status != 0) {
        fprintf(stderr, "Failed to get current RX timestamp: %s\n", bladerf_strerror(status));
        return -1;
    }
    
    d_tx_meta.timestamp = d_rx_meta.timestamp;
    //schedule tx and tx in the future
    d_tx_meta.timestamp += d_ts_inc_send;
    d_rx_meta.timestamp += d_ts_inc_recv;

    //Create sending and receiving threads
    std::thread sendThread(&BladerfDevice::send, this);
    std::thread recvThread(&BladerfDevice::recv, this);
    
    // Wait for threads to complete
    sendThread.join();
    recvThread.join();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    d_pulse_time = d_pulse_time + std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count();
    return 0;
}

struct bladerf* BladerfDevice::get_device_handler(){
    if(device == nullptr){
        std::cout << "WARNING, device is not initialised yet" << std::endl;
    }
    return device;
}

int BladerfDevice::set_gain(bladerf_gain gain, bladerf_channel ch){
    std::cout << "set gain of channel "<< ch << " to: " << gain << std::endl;
    int status = bladerf_set_gain(device, ch, gain);
    return status;
}

