/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "bladerfRadarMIMO_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>
#include <gnuradio/math.h>

namespace gr {
namespace sfcwRadar {

using input_type = gr_complex;
using output_type = gr_complex;
bladerfRadarMIMO::sptr bladerfRadarMIMO::make(bladerf_frequency start_freq,
                                              int num_steps,
                                              bladerf_frequency freq_step,
                                              int samp_rate,
                                              bladerf_gain rx_gain,
                                              bladerf_gain tx_gain,
                                              bladerf_gain ref_gain,
                                              size_t burst_len,
                                              size_t num_buffers,
                                              size_t buffer_size,
                                              size_t num_transfers,
                                              float cw_amplitude,
                                              float cw_frequency)
{
    return gnuradio::make_block_sptr<bladerfRadarMIMO_impl>(start_freq,
                                                            num_steps,
                                                            freq_step,
                                                            samp_rate,
                                                            rx_gain,
                                                            tx_gain,
                                                            ref_gain,
                                                            burst_len,
                                                            num_buffers,
                                                            buffer_size,
                                                            num_transfers,
                                                            cw_amplitude,
                                                            cw_frequency);
}


/*
 * The private constructor
 */
bladerfRadarMIMO_impl::bladerfRadarMIMO_impl(bladerf_frequency start_freq,
                                             int num_steps,
                                             bladerf_frequency freq_step,
                                             int samp_rate,
                                             bladerf_gain rx_gain,
                                             bladerf_gain tx_gain,
                                             bladerf_gain ref_gain,
                                             size_t burst_len,
                                             size_t num_buffers,
                                             size_t buffer_size,
                                             size_t num_transfers,
                                             float cw_amplitude,
                                             float cw_frequency)
    : gr::tagged_stream_block(
          "bladerfRadarMIMO",
          gr::io_signature::make(
              2 /* min inputs */, 2 /* max inputs */, sizeof(input_type)),
          gr::io_signature::make(
              2 /* min outputs */, 2 /*max outputs */, sizeof(output_type)),
          "burst")
{
    
    /**
     * register the message port
     * the module starts sweep the frequencies upon reception of a "scan" message
     * */
    message_port_register_in(pmt::mp("scan"));
    set_msg_handler(pmt::mp("scan"),[this](const pmt::pmt_t& msg){handle_scan_msg(msg);});

    /**
    * save input parameters
    * */
    d_start_freq = start_freq;
    d_freq_step = freq_step;
    d_currrent_freq = start_freq;
    d_num_steps = num_steps;
    d_max_freq = d_start_freq + d_freq_step * (num_steps-1);
    d_freq_index = 0;
    d_samp_rate = samp_rate;
    d_tx_gain = tx_gain;
    d_rx_gain = rx_gain;
    d_ref_gain = ref_gain;
    std::cout << "start_freq: " << d_start_freq << std::endl;
    std::cout << "freq_step: " << d_freq_step << std::endl;
    std::cout << "num_steps: " << d_num_steps << std::endl;
    std::cout << "max_freq: " << d_max_freq << std::endl; 
    std::cout << "samp_rate: " << samp_rate << std::endl; 

    d_burst_len = burst_len;
    std::cout << "burst_len: " << d_burst_len << std::endl;

    d_num_buffers = num_buffers;
    d_buffer_size = buffer_size;
    d_num_transfers = num_transfers;
    std::cout << "buffer setup. num_buffers: " << d_num_buffers << " buffer_size: " << buffer_size << " num_transfers: " << num_transfers << std::endl;

    d_cw_amplitude = cw_amplitude;
    d_cw_frequency = cw_frequency;

    int status = init_device();

    /**
     * Set input/ouput contrains based on the burst_len
     * */
    // two RXs
    set_output_multiple(2);
    // each RX output d_burst_len number of samples every time the work function is called
    set_min_noutput_items(d_burst_len);
    set_min_output_buffer(d_burst_len*2);
}

int bladerfRadarMIMO_impl::init_device(){

    d_scan = false;
    d_continuous_scan_flag = false;
    d_currrent_freq = d_start_freq;
    d_max_freq = d_start_freq + d_freq_step * (d_num_steps-1);

    /**
     * variables to save the quick retune parameters of each frequency step 
     * */
    d_quick_tunes_tx = new bladerf_quick_tune_info[d_num_steps];
    d_quick_tunes_rx = new bladerf_quick_tune_info[d_num_steps]; 
    d_freq_index = 0;
    
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
        if (bladerf_is_fpga_configured(dev)==1){
            std::cout << "FPGA is already loaded" << std::endl;
        }else{
            std::cerr << "FPGA not loaded" << std::endl;
        }

        /**
         * set tunning mode to FPGA to get fast frequency tunning
         * */
        bladerf_set_tuning_mode(dev, BLADERF_TUNING_MODE_FPGA);
        bladerf_tuning_mode current_mode;
        bladerf_get_tuning_mode(dev, &current_mode);
        std::cout << "tnning mode is: " << current_mode << std::endl;
        
        /**
         * Configure RX channel 0. 
         * RX channel 1 is used for receiving echo signals
         * */
        config.channel = BLADERF_CHANNEL_RX(0);
        config.frequency = d_start_freq;
        config.bandwidth = d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_rx_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "RX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "RX channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        
        /**
         * Configure RX channel 1
         * This channel is used for receiving ref signal (from a spliter or ditectional coupler)
         * */
        config.channel = BLADERF_CHANNEL_RX(1);
        config.frequency = d_start_freq;
        config.bandwidth = d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_ref_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "RX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "RX channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        /**
         * Configure TX channel 0
         * This channel is used for sending radar signal 
         * */
        config.channel = BLADERF_CHANNEL_TX(0);
        config.frequency = d_start_freq;
        config.bandwidth = d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_tx_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "TX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "TX channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        /**
         * Configure TX channel 1
         * This channel is used for sending ref signal (from a spliter or ditectional coupler)
         * */
        config.channel = BLADERF_CHANNEL_TX(1);
        config.frequency = d_start_freq;
        config.bandwidth = d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_ref_gain;
        status = configure_channel(dev,&config);
        if (status !=0){
            std::cerr << "TX Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "TX channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        
        /* Initialize synchronous interface on RXs and TXs */
        status = init_sync(dev);
        if (status != 0) {
            fprintf(stderr, "Failed to enable RX: %s\n", bladerf_strerror(status));
        }else{
            std::cout << "init succed" << std::endl;
        }
        
        /**
         * get quick retune parameters of each frequency step for RX and TX
         * The parameters are stored in d_quick_tunes_tx and d_quick_tunes_rx respectively
         * */
        status = set_quick_tune();
        if(status == 0){
            std::cout << "set quick tune finished" << std::endl;
        }
    }
    return status;
}

int bladerfRadarMIMO_impl::configure_channel(struct bladerf *dev, struct channel_config *c){
    int status;
    /**
     * Set LO frequency
     * */
    status = bladerf_set_frequency(dev, c->channel, c->frequency);
    if (status != 0) {
        fprintf(stderr, "Failed to set frequency = %u: %s\n", c->frequency,
        bladerf_strerror(status));
        return status;
    }
    bladerf_frequency current_freq;
    status = bladerf_get_frequency(dev, c->channel, &current_freq);
    if(status!=0){
        std::cerr<<"Failed to read frequency from Channel: " << c->channel << std::endl;
    }else{
        std::cout << "Set chennel" << c->channel << ", frequency: " << current_freq << std::endl;
    }

    /**
     * Set sampling rate
     * */
    unsigned int actual_value;
    status = bladerf_set_sample_rate(dev, c->channel, c->samplerate, &actual_value);
    if (status != 0) {
        fprintf(stderr, "Failed to set samplerate = %u: %s\n", c->samplerate,
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "Set chennel" << c->channel << ", samplerate: " << actual_value << std::endl;
    }

    status = bladerf_set_gain_mode(dev, c->channel, BLADERF_GAIN_MANUAL);
    //status = bladerf_set_gain_mode(dev, c->channel, BLADERF_GAIN_HYBRID_AGC);
    //status = bladerf_set_gain_mode(dev, c->channel, BLADERF_GAIN_SLOWATTACK_AGC);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode = %u: %s\n", c->channel,
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "Set chennel" << c->channel << ", gain mode: " << BLADERF_GAIN_MANUAL << std::endl;
    }

    bladerf_gain_mode current_gain_mode;
    status = bladerf_get_gain_mode(dev, c->channel, &current_gain_mode);
    if(status!=0){
        std::cerr << "Falied to read gain mode from channel: " << c->channel << std::endl;
    }else{
        std::cout << "Channel: " << c->channel << ", gain mode: " << current_gain_mode << std::endl;
    }

    /*const bladerf_range *range;
    status = bladerf_get_gain_range(dev, c->channel, &range);
    if(status != 0){
        fprintf(stderr, "Failed to get gain range, channel: %u: %s\n", c->channel,
        bladerf_strerror(status));
        return status;
    }
    std::cout << "gain range: " << range->min << ": " << range->max << std::endl;
    std::cout << "gain scale: " << range->scale << std::endl;
    std::cout << "gain step: " << range->step << std::endl;*/

    /**
     * Set gain
     * */
    std::cout << "trying to set gain: " << c->gain << std::endl;
    status = bladerf_set_gain(dev, c->channel, c->gain);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain: %s\n", bladerf_strerror(status));
        return status;
    }

    return status; 
}

int bladerfRadarMIMO_impl::init_sync(struct bladerf *dev){
    int status;
 
    /* Configure both the device's X2 RX and X2 TX channels for use with the
    * synchronous
    * interface. SC16 Q11 samples *without* metadata are used. */
 
    status = bladerf_sync_config(dev, BLADERF_RX_X2, 
                                 BLADERF_FORMAT_SC16_Q11, d_num_buffers, 
                                 d_buffer_size, d_num_transfers,timeout_ms);

    if (status != 0) {
        fprintf(stderr, "Failed to configure RX sync interface: %s\n",
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "RX configured. num_buffers:  "<< d_num_buffers 
            << ", buffer_size: " << d_buffer_size 
            << ", num_transfers: " << d_num_transfers 
            << ", timeout_ms: " << timeout_ms << std::endl;
    }
 
    status = bladerf_sync_config(dev, BLADERF_TX_X2,
                                 BLADERF_FORMAT_SC16_Q11, d_num_buffers,
                                 d_buffer_size, d_num_transfers, timeout_ms); 
    if (status != 0) {
        fprintf(stderr, "Failed to configure TX sync interface: %s\n",
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "TX configured. num_buffers:  "<< d_num_buffers 
            << ", buffer_size: " << d_buffer_size 
            << ", num_transfers: " << d_num_transfers 
            << ", timeout_ms: " << timeout_ms << std::endl;
    }
    
    /**
     * Enable bias tee of RX_0
     * */
    /*status = bladerf_set_bias_tee(dev, BLADERF_CHANNEL_RX(0), true);
    if(status != 0){
        std::cerr << "set channel: " << BLADERF_CHANNEL_RX(0) << " bias tee failed" << std::endl;
    }else{
        bool is_bias_tee_enabled = false;
        status = bladerf_get_bias_tee(dev, BLADERF_CHANNEL_RX(0), &is_bias_tee_enabled);
        std::cout << "bias tee status of chennel " << BLADERF_CHANNEL_RX(0) << " :" << is_bias_tee_enabled << std::endl;
    }*/

    /**
     * Set AGC of RX_0 (echo)
     * */
    status = bladerf_set_gain_mode(dev, BLADERF_CHANNEL_RX(0), BLADERF_GAIN_MANUAL);
    //status = bladerf_set_gain_mode(dev, BLADERF_CHANNEL_RX(0), BLADERF_GAIN_HYBRID_AGC);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode = %u: %s\n", BLADERF_CHANNEL_RX(0),
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "Set chennel" << BLADERF_CHANNEL_RX(0) << ", gain mode" << std::endl;
    }

    bladerf_gain_mode current_gain_mode;
    status = bladerf_get_gain_mode(dev, BLADERF_CHANNEL_RX(0), &current_gain_mode);
    if(status!=0){
        std::cerr << "Falied to read gain mode from channel: " << BLADERF_CHANNEL_RX(0) << std::endl;
    }else{
        std::cout << "Channel: " << BLADERF_CHANNEL_RX(0) << ", gain mode: " << current_gain_mode << std::endl;
    } 
    
    /**
     * Set AGC for RX_1 (ref)
     * */
    //status = bladerf_set_gain_mode(dev, BLADERF_CHANNEL_RX(1), BLADERF_GAIN_MANUAL);
    status = bladerf_set_gain_mode(dev, BLADERF_CHANNEL_RX(1), BLADERF_GAIN_HYBRID_AGC);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode = %u: %s\n", BLADERF_CHANNEL_RX(1),
        bladerf_strerror(status));
        return status;
    }else{
        std::cout << "Set chennel" << BLADERF_CHANNEL_RX(1) << ", gain mode: " << BLADERF_GAIN_MANUAL << std::endl;
    }

    status = bladerf_get_gain_mode(dev, BLADERF_CHANNEL_RX(1), &current_gain_mode);
    if(status!=0){
        std::cerr << "Falied to read gain mode from channel: " << BLADERF_CHANNEL_RX(1) << std::endl;
    }else{
        std::cout << "Channel: " << BLADERF_CHANNEL_RX(1) << ", gain mode: " << current_gain_mode << std::endl;
    }

    /**
     * Enable bias tee for TX0
     * */
    /*status = bladerf_set_bias_tee(dev, BLADERF_CHANNEL_TX(0), true);
    if(status != 0){
        std::cerr << "set channel: " << BLADERF_CHANNEL_TX(0) << " bias tee failed" << std::endl;
    }else{
        bool is_bias_tee_enabled = false;
        status = bladerf_get_bias_tee(dev, BLADERF_CHANNEL_TX(0), &is_bias_tee_enabled);
        std::cout << "bias tee status of chennel " << BLADERF_CHANNEL_TX(0) << " :" << is_bias_tee_enabled << std::endl;
    }*/

    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(0), true);
    if (status != 0) {
        std::cerr << "RX 0 enable failed" << std::endl;
        return status;
    }else{
        std::cout << "RX 0 enalbed" << std::endl;
    }
    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(1), true);
    if (status != 0) {
        std::cerr << "RX 1 enable failed" << std::endl;
        return status;
    }else{
        std::cout << "RX 1 enalbed" << std::endl;
    }
    status = bladerf_enable_module(dev, BLADERF_CHANNEL_TX(0), true);
    if (status != 0) {
        std::cerr << "TX 0 enable failed" << std::endl;
        return status;
    }else{
        std::cout << "TX 0 enalbed" << std::endl;
    } 
    status = bladerf_enable_module(dev, BLADERF_CHANNEL_TX(1), true);
    if (status != 0) {
        std::cerr << "TX 1 enable failed" << std::endl;
        return status;
    }else{
        std::cout << "TX 1 enalbed" << std::endl;
    } 
    
    /**
     * varify if the gains of each channel is correctly assigned
     * */
    bladerf_gain current_gain;
    status = bladerf_get_gain(dev,BLADERF_CHANNEL_RX(0),&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << BLADERF_CHANNEL_RX(0) << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << BLADERF_CHANNEL_RX(0) << ", gain: " << current_gain << std::endl;
    }
    
    status = bladerf_get_gain(dev,BLADERF_CHANNEL_RX(1),&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << BLADERF_CHANNEL_RX(1) << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << BLADERF_CHANNEL_RX(1) << ", gain: " << current_gain << std::endl;
    }
    
    status = bladerf_get_gain(dev,BLADERF_CHANNEL_TX(0),&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << BLADERF_CHANNEL_TX(0) << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << BLADERF_CHANNEL_TX(0) << ", gain: " << current_gain << std::endl;
    }
    
    status = bladerf_get_gain(dev,BLADERF_CHANNEL_TX(1),&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << BLADERF_CHANNEL_TX(1) << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << BLADERF_CHANNEL_TX(1) << ", gain: " << current_gain << std::endl;
    }

    /* Allocate memory for conversions in work() */
    size_t alignment = volk_get_alignment();

    /**
     * Bladerf accept int16_t as input and output samples in int16_t while gnuradio use 2x float to store one sample 
     * */
    //Because we use two RXs, the size of input samples are interleaved so the buffer for sending should be twice as the d_burst_len
    _16icbuf_in = reinterpret_cast<int16_t *>(volk_malloc(2*2*d_burst_len*sizeof(int16_t), alignment));
    _32fcbuf_in = reinterpret_cast<gr_complex *>(volk_malloc(2*d_burst_len*sizeof(gr_complex), alignment));

    //Because we use two RXs, the size of output samples are interleaved so the buffer for receiving should be twice as the sending buffer
    _16icbuf_out = reinterpret_cast<int16_t *>(volk_malloc(2*2*d_burst_len*sizeof(int16_t), alignment));
    _32fcbuf_out = reinterpret_cast<gr_complex *>(volk_malloc(2*d_burst_len*sizeof(gr_complex), alignment)); 

    return status;
}

int bladerfRadarMIMO_impl::set_quick_tune(){
    int status;
    for (int i = 0; i < d_num_steps; i++){
        std::cout << "set quick tune parameters for frequency: " << d_currrent_freq << std::endl;
        status = bladerf_set_frequency(dev, BLADERF_MODULE_TX, d_currrent_freq);
        if(status!=0){
            std::cerr << "set TX frequency to: "<< d_currrent_freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_tx[i].freq = d_currrent_freq;
        status = bladerf_get_quick_tune(dev, BLADERF_MODULE_TX, &d_quick_tunes_tx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for TX" << std::endl;
            return status;
        }
        
        status = bladerf_set_frequency(dev, BLADERF_MODULE_RX, d_currrent_freq);
        if(status!=0){
            std::cerr << "set RX frequency to: "<< d_currrent_freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_rx[i].freq = d_currrent_freq;
        status = bladerf_get_quick_tune(dev, BLADERF_MODULE_RX, &d_quick_tunes_rx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for RX" << std::endl;
            return status;
        }
        d_currrent_freq = d_currrent_freq + d_freq_step;
    }

    /**
     * set d_currrent_freq to start frequency and frequency index to 0
     * Upon receiving "scan" message, the module can imediately start sweep the frequencies 
     * */
    d_currrent_freq = d_start_freq;
    d_freq_index = 0;
    return status;
}

/*
 * Our virtual destructor.
 */
bladerfRadarMIMO_impl::~bladerfRadarMIMO_impl() {
    bladerf_close(dev);
}

int bladerfRadarMIMO_impl::calculate_output_stream_length(
    const gr_vector_int& ninput_items)
{
    int noutput_items = 0;
    return noutput_items;
}

/**
 * receive samples from two RXs, and store the received samples in _16icbuf_out
 * we are expecting to receive d_num_samples_to_recv samples, the size is twice of the busrt_len
 * as the samples from two RXs are interleaved
 * */
void bladerfRadarMIMO_impl::recv(){
    int status;
    status = bladerf_sync_rx(dev, static_cast<void *>(_16icbuf_out),
            d_num_samples_to_recv, NULL, timeout_ms*2);

    if (status != 0){
        std::cerr << "receiving failed: " << bladerf_strerror(status) << std::endl;
    }
}

int bladerfRadarMIMO_impl::quick_tune(int index){
    if(index >= d_num_steps){
        std::cerr << "invalid index" << std::endl;
        return -1;
    }

    //std::cout<<"tunning tx to: " << d_quick_tunes_tx[index].freq << std::endl;
    int status = bladerf_schedule_retune(dev, BLADERF_MODULE_TX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_tx[index].quick_tune);
    if(status != 0){
        std::cerr << "failed to tune TX: " << bladerf_strerror(status) << std::endl;
        return status;
    }

    //std::cout<<"tunning rx to: " << d_quick_tunes_rx[index].freq << std::endl;
    status = bladerf_schedule_retune(dev, BLADERF_MODULE_RX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_rx[index].quick_tune);
    if(status != 0){
        std::cerr << "failed to tune RX: " << bladerf_strerror(status) << std::endl;
        return status;
    }
    return status;
}

/**
 * send the samples stored in _16icbuf_in
 * sending through tow tx ports, the number of samples to send equals to the burst_len x 2
 * */
void bladerfRadarMIMO_impl::send(){
    int status;

    status = bladerf_sync_tx(dev, static_cast<void const *>(_16icbuf_in), d_num_samples_to_send, NULL, timeout_ms*2); 

    if (status != 0){
        std::cerr << "sending failed: " << bladerf_strerror(status) << std::endl;
    }
}

void bladerfRadarMIMO_impl::update_gps(){
    d_gps_x = d_gps_x + 1.0;
}

void bladerfRadarMIMO_impl::generate_cw_samples(){
    //gr_complex d_phase = 0;

    memset(_32fcbuf_in,0,d_burst_len*2*sizeof(gr_complex));
    for (int i=0;i<d_burst_len*2;i++){
        _32fcbuf_in[i] += d_cw_amplitude*exp(d_phase);
        _32fcbuf_in[i+1] += _32fcbuf_in[i];
        i++;
        d_phase = gr_complex(0,std::fmod(imag(d_phase) + 2 * GR_M_PI * d_cw_frequency / (float)d_samp_rate,2*GR_M_PI));
    }
}

void bladerfRadarMIMO_impl::handle_scan_msg(const pmt::pmt_t& msg){
    std::cout << "received scan cmd" << std::endl;
    std::cout << pmt::cdr(msg) << std::endl;
    if ((pmt::to_long(pmt::cdr(msg)) == 1)){
        d_scan = true;
        d_continuous_scan_flag = false;
    }else if ((pmt::to_long(pmt::cdr(msg)) == 2)){
        d_scan = true;
        d_continuous_scan_flag = true;
    }
}

int bladerfRadarMIMO_impl::work(int noutput_items,
                                gr_vector_int& ninput_items,
                                gr_vector_const_void_star& input_items,
                                gr_vector_void_star& output_items)
{
    if (d_scan == true){
    //std::cout << "tune to next freq:" << d_currrent_freq << std::endl;
        //std::cout << "start scanning... current_freq: " << d_currrent_freq << std::endl;
        if(d_currrent_freq > d_max_freq){
            end = std::chrono::steady_clock::now();
            std::cout << "Time used = " << std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count() << "[µs]" << std::endl; 
            std::cout << "reach max freq, tune back to :" << d_start_freq << std::endl;
            d_currrent_freq = d_start_freq;
            d_freq_index = 0;
            if(d_continuous_scan_flag == false){
                d_scan = false;
            }
            //d_scan = false;
            begin = std::chrono::steady_clock::now();
            return 0;
        }

        /*int status = bladerf_set_frequency(dev, BLADERF_MODULE_TX, d_currrent_freq);
        if (status != 0) {
            fprintf(stderr, "Failed to set frequency = %u: %s\n", BLADERF_CHANNEL_TX(0),
                bladerf_strerror(status));
        }

        //status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(0), d_currrent_freq);
        status = bladerf_set_frequency(dev, BLADERF_MODULE_RX, d_currrent_freq);
        if (status != 0) {
            fprintf(stderr, "Failed to set frequency = %u: %s\n", BLADERF_CHANNEL_RX(0),
                bladerf_strerror(status));

        }*/
        
        //std::cout << "prepare to send cw in frequency: " << d_quick_tunes_tx[d_freq_index].freq << ", freq_index = " << d_freq_index << std::endl;
        //std::cout << "prepare to recv cw in frequency: " << d_quick_tunes_rx[d_freq_index].freq << ", freq_index = " << d_freq_index << std::endl;
        quick_tune(d_freq_index);
        
    }else{
        //do nothing if no "scan" message received
        return 0;
    }
    
    //we will fall here if a "scan" message was received
    //std::cout << "number of inputs from upstream: " << ninput_items[0] << std::endl;
    noutput_items = ninput_items[0];
    d_num_samples_to_send = ninput_items[0]*2;
    d_num_samples_to_recv = ninput_items[0]*2;
    
    //add a frequency tag
    //pmt::pmt_t current_freq_tag_key = pmt::string_to_symbol("c_freq");
    //pmt::pmt_t current_freq_tag_value = pmt::from_uint64(d_currrent_freq);
    //add_item_tag(0,nitems_written(0),current_freq_tag_key,current_freq_tag_value);

    //add gps tag
    if(d_freq_index == 0){
        update_gps();
        pmt::pmt_t current_gps_tag_key = pmt::string_to_symbol("c_gps");
        pmt::pmt_t gps_x = pmt::from_double(d_gps_x);
        pmt::pmt_t gps_y = pmt::from_double(d_gps_y);
        pmt::pmt_t current_gps_tag_value = pmt::make_tuple(gps_x,gps_y);
        add_item_tag(0,nitems_written(0),current_gps_tag_key, current_gps_tag_value);
        //add a new scan tag
        pmt::pmt_t new_scan_tag_key = pmt::string_to_symbol("newScan");
        pmt::pmt_t new_scan_tag_value = pmt::PMT_T;
        add_item_tag(0,nitems_written(0),new_scan_tag_key,new_scan_tag_value);
        //pmt::pmt_t current_freq_tag_key = pmt::string_to_symbol("c_freq");
        //pmt::pmt_t current_freq_tag_value = pmt::from_uint64(d_currrent_freq);
        //add_item_tag(0,nitems_written(0),current_freq_tag_key,current_freq_tag_value);
    }

    /**
     * transmit samples created by upstream signal generator
     *
     * */
    /*gr_complex const **in = reinterpret_cast<gr_complex const **>(&input_items[0]); 
    
    // we need to interleave the streams as we copy
    gr_complex *intl_out = _32fcbuf_in;

    for (size_t i = 0; i < (noutput_items/2); ++i) {
      for (size_t n = 0; n < 2; ++n) {
        memcpy(intl_out++, in[n]++, sizeof(gr_complex));
      }
    }*/

    generate_cw_samples();
    
    // convert floating point to fixed point and scale
    // input_items is gr_complex (2x float), so num_points is 2*noutput_items
    volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
                            SCALING_FACTOR, 2*d_num_samples_to_send);

    /**
     * create sending and receiving threads
     * */
    //std::cout << "sending cw in frequency: " << d_currrent_freq << ", freq_index = " << d_freq_index << std::endl;
    d_thread_recv = gr::thread::thread(boost::bind(&bladerfRadarMIMO_impl::recv, this)); 
    d_thread_send = gr::thread::thread(boost::bind(&bladerfRadarMIMO_impl::send, this));
    
    // Wait for threads to complete
    d_thread_recv.join();
    d_thread_send.join();
    
    /**
     * process received samples
     * */
    // convert from int16_t to float
    // output_items is gr_complex (2x float), so num_points is 2*noutput_items
    volk_16i_s32f_convert_32f(reinterpret_cast<float *>(_32fcbuf_out), _16icbuf_out,
                            SCALING_FACTOR, 2*d_num_samples_to_recv);

    // copy the samples into output_items
    gr_complex **out = reinterpret_cast<gr_complex **>(&output_items[0]); 

    // we need to deinterleave the multiplex as we copy
    gr_complex const *deint_in = _32fcbuf_out;

    for (size_t i = 0; i < (d_num_samples_to_recv/2); ++i) {
        for (size_t n = 0; n < 2; ++n) {
           memcpy(out[n]++, deint_in++, sizeof(gr_complex));
        }
    }
    
    //jump to the next frequency when the work function is called again
    d_currrent_freq = d_currrent_freq + d_freq_step;
    d_freq_index ++;
    
    return d_num_samples_to_recv/2;
}

} /* namespace sfcwRadar */
} /* namespace gr */
