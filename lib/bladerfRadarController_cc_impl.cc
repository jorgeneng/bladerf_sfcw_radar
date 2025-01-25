/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "bladerfRadarController_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>
#include <gnuradio/math.h>

namespace gr {
namespace sfcwRadar {

using output_type = gr_complex;
bladerfRadarController_cc::sptr
bladerfRadarController_cc::make(bladerf_frequency start_freq,
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
                                float cw_frequency,
                                float ts_inc_send,
                                float ts_inc_recv,
                                float ts_inc_tune)
{
    return gnuradio::make_block_sptr<bladerfRadarController_cc_impl>(start_freq,
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
                                                                     cw_frequency,
                                                                     ts_inc_send,
                                                                     ts_inc_recv,
                                                                     ts_inc_tune);
}


/*
 * The private constructor
 */
bladerfRadarController_cc_impl::bladerfRadarController_cc_impl(
    bladerf_frequency start_freq,
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
    float cw_frequency,
    float ts_inc_send,
    float ts_inc_recv,
    float ts_inc_tune)
    : gr::sync_block("bladerfRadarController_cc",
                     gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(
                         2 /* min outputs */, 2 /*max outputs */, sizeof(output_type)))
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

    /* Set up constraints */
    int const alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
    set_alignment(std::max(1,alignment_multiple)); 
    
    /* Allocate memory for conversions in work() */
    size_t alignment = volk_get_alignment();
    /**
     * Bladerf accept int16_t as input and output samples in int16_t while gnuradio use 2x float to store one sample 
     * */
    //Because we use two TXs, the size of input samples are interleaved so the buffer for sending should be twice as the d_burst_len
    _16icbuf_in = reinterpret_cast<int16_t *>(volk_malloc(2*2*d_burst_len*sizeof(int16_t), alignment));
    _32fcbuf_in = reinterpret_cast<gr_complex *>(volk_malloc(2*d_burst_len*sizeof(gr_complex), alignment));

    //Because we use two RXs, the size of output samples are interleaved so the buffer for receiving should be twice as the d_burst_len
    _16icbuf_out = reinterpret_cast<int16_t *>(volk_malloc(2*2*d_burst_len*sizeof(int16_t), alignment));
    _32fcbuf_out = reinterpret_cast<gr_complex *>(volk_malloc(2*d_burst_len*sizeof(gr_complex), alignment)); 

    int status = init_device();
    /**
     * Set input/ouput contrains based on the burst_len
     * */
    // two RXs
    set_output_multiple(2);
    set_min_noutput_items(d_burst_len*num_steps);
    set_min_output_buffer(d_burst_len*num_steps*2);

}


int bladerfRadarController_cc_impl::init_device(){

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

int bladerfRadarController_cc_impl::configure_channel(struct bladerf *dev, struct channel_config *c){
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

int bladerfRadarController_cc_impl::init_sync(struct bladerf *dev){
    int status;
 
    /* Configure both the device's X2 RX and X2 TX channels for use with the
    * synchronous
    * interface. SC16 Q11 samples *with* metadata are used. */
 
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

    return status;
}

int bladerfRadarController_cc_impl::set_quick_tune(){
    int status;
    for (int i = 0; i < d_num_steps; i++){
        std::cout << "set quick tune parameters for frequency: " << d_currrent_freq << std::endl;
        status = bladerf_set_frequency(dev, BLADERF_TX, d_currrent_freq);
        if(status!=0){
            std::cerr << "set TX frequency to: "<< d_currrent_freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_tx[i].freq = d_currrent_freq;
        status = bladerf_get_quick_tune(dev, BLADERF_TX, &d_quick_tunes_tx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for TX" << std::endl;
            return status;
        }
        
        status = bladerf_set_frequency(dev, BLADERF_RX, d_currrent_freq);
        if(status!=0){
            std::cerr << "set RX frequency to: "<< d_currrent_freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_rx[i].freq = d_currrent_freq;
        status = bladerf_get_quick_tune(dev, BLADERF_RX, &d_quick_tunes_rx[i].quick_tune);
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

int bladerfRadarController_cc_impl::wait_for_timestamp(struct bladerf *dev, bladerf_direction dir, uint64_t timestamp, unsigned int timeout_ms){
    //std::cout<<"wait for timestamp" << std::endl;
    int status;
    uint64_t curr_ts = 0;
    unsigned int slept_ms = 0;
    bool done;
    do{
        status = bladerf_get_timestamp(dev, dir, &curr_ts);
        done = (status!=0) || curr_ts >= timestamp;
        if(!done){
            if(slept_ms > timeout_ms){
                done = true;
                status = BLADERF_ERR_TIMEOUT;
            }else{
                usleep(10000);
                slept_ms += 10;
            }
        }
    }while(!done);
    //std::cout<<"wait for timestamp finished" << std::endl;
    return status;
}

/*
 * Our virtual destructor.
 */
bladerfRadarController_cc_impl::~bladerfRadarController_cc_impl() {
    bladerf_close(dev);
    volk_free(_16icbuf_in);
    volk_free(_16icbuf_out);
    volk_free(_32fcbuf_in);
    volk_free(_32fcbuf_out);
    _16icbuf_in = NULL;
    _16icbuf_out = NULL;
    _32fcbuf_in = NULL;
    _32fcbuf_out = NULL;
}

void bladerfRadarController_cc_impl::generate_cw_samples(){
    //gr_complex d_phase = 0;

    memset(_32fcbuf_in,0,d_burst_len*2*sizeof(gr_complex));
    for (size_t i=0;i<d_burst_len*2;i++){
        _32fcbuf_in[i] += d_cw_amplitude*exp(d_phase);
        _32fcbuf_in[i+1] += _32fcbuf_in[i];
        i++;
        d_phase = gr_complex(0,std::fmod(imag(d_phase) + 2 * GR_M_PI * d_cw_frequency / (float)d_samp_rate,2*GR_M_PI));
    }
}

void bladerfRadarController_cc_impl::handle_scan_msg(const pmt::pmt_t& msg){
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

/**
 * send the samples stored in _16icbuf_in
 * sending through tow tx ports, the number of samples to send equals to the burst_len x 2
 * */
void bladerfRadarController_cc_impl::send(){
    int status;
    
    /*struct bladerf_metadata meta;
    memset(&meta, 0, sizeof(meta));

    meta.flags = BLADERF_META_FLAG_TX_BURST_START | BLADERF_META_FLAG_TX_BURST_END | BLADERF_META_FLAG_TX_NOW; */

    //Retrieve the current timestamp so we can schedule our transmission in the future.
    /*status = bladerf_get_timestamp(dev, BLADERF_TX, &meta.timestamp);
    if (status != 0) {
        fprintf(stderr, "Failed to get current TX timestamp: %s\n",
                bladerf_strerror(status));
    } else {
        //std::cout << "Current TX timestamp " << meta.timestamp << std::endl; 
    } 

    // Set initial timestamp d_ts_inc_send ms in the future.
    meta.timestamp += d_ts_inc_send;*/

    /*status = bladerf_sync_tx(dev, static_cast<void const *>(_16icbuf_in), d_burst_len*2*2, &meta, timeout_ms*2); 

    if (status == 0){
        status = bladerf_get_timestamp(dev, BLADERF_TX, &meta.timestamp);
        if (status != 0) {
            fprintf(stderr, "Failed to get current TX timestamp: %s\n",
                    bladerf_strerror(status));
        }

        meta.timestamp += d_burst_len;
        wait_for_timestamp(dev, BLADERF_TX, meta.timestamp, timeout_ms);
    }
    else{
        std::cerr << "sending failed: " << bladerf_strerror(status) << std::endl;
    }*/

    status = bladerf_sync_tx(dev, static_cast<void const *>(_16icbuf_in), d_burst_len*2, NULL, timeout_ms*2); 

    if (status != 0){
        std::cerr << "sending failed: " << bladerf_strerror(status) << std::endl;
    }
}

/**
 * receive samples from two RXs, and store the received samples in _16icbuf_out
 * we are expecting to receive d_num_samples_to_recv samples, the size is twice of the busrt_len
 * as the samples from two RXs are interleaved
 * */
void bladerfRadarController_cc_impl::recv(){
    int status;
    /**
     * scheduled receiving
     * */
    /*struct bladerf_metadata meta;
    memset(&meta,0,sizeof(meta));
    //ensure BLADERF_META_FLAG_RX_NOW is cleared
    meta.flags = 0;
    meta.flags = BLADERF_META_FLAG_RX_NOW;*/

    //Retrieve the current timestamp 
    /*status = bladerf_get_timestamp(dev, BLADERF_RX, &meta.timestamp);
    if (status != 0) {
        fprintf(stderr, "Failed to get current RX timestamp: %s\n",
                bladerf_strerror(status));
    } else {
        //std::cout << "Current RX timestamp " << meta.timestamp << std::endl; 
    } 

    //schedule first RX to be d_ts_inc_rec ms in the future.
    meta.timestamp += d_ts_inc_rec;*/

    /*status = bladerf_sync_rx(dev, static_cast<void *>(_16icbuf_out),
            d_burst_len*2*2, &meta, timeout_ms*2);

    if (status != 0){
        std::cerr << "receiving failed: " << bladerf_strerror(status) << std::endl;
    }else if (meta.status & BLADERF_META_STATUS_OVERRUN){
        std::cerr << "Overrun detected in scheduled RX. Number of samples read is: " << meta.actual_count << std::endl;
    }*/
    
    status = bladerf_sync_rx(dev, static_cast<void *>(_16icbuf_out),
            d_burst_len*2, NULL, timeout_ms*2);

    if (status != 0){
        std::cerr << "receiving failed: " << bladerf_strerror(status) << std::endl;
    }
    //memcpy(_16icbuf_out, _16icbuf_in, d_burst_len*2*2*sizeof(int16_t));
    //memcpy(_32fcbuf_out, _32fcbuf_in, d_burst_len*2*sizeof(gr_complex));
}

void bladerfRadarController_cc_impl::tune_rx(){

    //std::cout<<"tunning rx to: " << d_quick_tunes_rx[index].freq << std::endl;
    int status = bladerf_schedule_retune(dev, BLADERF_RX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_rx[d_freq_index].quick_tune);
    if(status != 0){
        std::cerr << "failed to tune RX: " << bladerf_strerror(status) << std::endl;
    }
}

void bladerfRadarController_cc_impl::tune_tx(){
    //std::cout<<"tunning tx to: " << d_quick_tunes_tx[index].freq << std::endl;
    int status = bladerf_schedule_retune(dev, BLADERF_TX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_tx[d_freq_index].quick_tune);
    //status = bladerf_set_frequency(dev, BLADERF_TX, d_quick_tunes_tx[index].freq);
    if(status != 0){
        std::cerr << "failed to tune TX: " << bladerf_strerror(status) << std::endl;
    }
}

int bladerfRadarController_cc_impl::quick_tune(){
    if(d_freq_index>= d_num_steps){
        std::cerr << "invalid index" << std::endl;
        return -1;
    }

    //std::cout<<"tunning rx to: " << d_quick_tunes_rx[index].freq << std::endl;
    int status = bladerf_schedule_retune(dev, BLADERF_RX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_rx[d_freq_index].quick_tune);
    //int status = bladerf_set_frequency(dev, BLADERF_RX, d_quick_tunes_rx[index].freq);
    if(status != 0){
        std::cerr << "failed to tune RX: " << bladerf_strerror(status) << std::endl;
        return status;
    }

    //std::cout<<"tunning tx to: " << d_quick_tunes_tx[index].freq << std::endl;
    //std::chrono::steady_clock::time_point tune_begin = std::chrono::steady_clock::now();
    status = bladerf_schedule_retune(dev, BLADERF_TX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_tx[d_freq_index].quick_tune);
    //std::chrono::steady_clock::time_point tune_end = std::chrono::steady_clock::now();
    //std::cout << "Time used for tuning = " << std::chrono::duration_cast<std::chrono::microseconds>(tune_end - tune_begin).count() << "[µs]" << std::endl;
    //status = bladerf_set_frequency(dev, BLADERF_TX, d_quick_tunes_tx[index].freq);
    if(status != 0){
        std::cerr << "failed to tune TX: " << bladerf_strerror(status) << std::endl;
        return status;
    }
    /*d_thread_rx_freq_tuning = gr::thread::thread(boost::bind(&bladerfRadarController_cc_impl::tune_rx, this));
    d_thread_tx_freq_tuning = gr::thread::thread(boost::bind(&bladerfRadarController_cc_impl::tune_tx, this));

    d_thread_rx_freq_tuning.join();
    d_thread_tx_freq_tuning.join();*/
    return 0;
}

int bladerfRadarController_cc_impl::work(int noutput_items,
                                         gr_vector_const_void_star& input_items,
                                         gr_vector_void_star& output_items)
{
    //auto out = static_cast<output_type*>(output_items[0]);
    gr_complex **out = reinterpret_cast<gr_complex **>(&output_items[0]);
    if(d_scan == true){
        std::cout << "scanning..." << std::endl;
        begin = std::chrono::steady_clock::now();
        //add a new scan tag
        pmt::pmt_t new_scan_tag_key = pmt::string_to_symbol("newScan");
        pmt::pmt_t new_scan_tag_value = pmt::PMT_T;
        add_item_tag(0,nitems_written(0),new_scan_tag_key,new_scan_tag_value);
        // scan cmd received, start sweeping the bandwidth
        for (int i = 0; i < d_num_steps; i++){
            //std::cout << "step " << i << std::endl;
            //1. tune frequency
            d_freq_index = i;
            quick_tune();
            //2. generate samples
            generate_cw_samples();
            //std::cout << "generate_cw_samples" << std::endl;
            // convert floating point to fixed point and scale
            // input_items is gr_complex (2x float), so num_points is 2*noutput_items
            volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
                            SCALING_FACTOR, 2*2*d_burst_len);
            //std::cout << "volk_32f_s32f_convert_16i" << std::endl;
            /**
            * create sending and receiving threads
            * */
            //std::cout << "sending cw in frequency: " << d_currrent_freq << ", freq_index = " << d_freq_index << std::endl;
            d_thread_recv = gr::thread::thread(boost::bind(&bladerfRadarController_cc_impl::recv, this)); 
            d_thread_send = gr::thread::thread(boost::bind(&bladerfRadarController_cc_impl::send, this));
    
            // Wait for threads to complete
            d_thread_recv.join();
            d_thread_send.join();
            //std::cout << "threads ended" << std::endl;
            /**
            * process received samples
            * */
            // convert from int16_t to float
            // output_items is gr_complex (2x float), so num_points is 2*noutput_items
            volk_16i_s32f_convert_32f(reinterpret_cast<float *>(_32fcbuf_out), _16icbuf_out,
                            SCALING_FACTOR, 2*2*d_burst_len);
            //std::cout << "process received samples" << std::endl;

            //std::cout << "copy the samples into output_items" <<std::endl;
            // we need to deinterleave the multiplex as we copy
            gr_complex const *deint_in = _32fcbuf_out;

            //std::cout << "deinterleave" << std::endl;
            for (size_t i = 0; i < (d_burst_len); ++i) {
                for (size_t n = 0; n < 2; ++n) {
                    memcpy(out[n]++, deint_in++, sizeof(gr_complex));
                }
            }
        }
        end = std::chrono::steady_clock::now();
        std::cout << "Time used = " << std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count() << "[µs]" << std::endl;
        if(d_continuous_scan_flag == false){
            d_scan = false;
        }
    }else{
        return 0;
    }
    //std::cout << "return: " << d_num_steps*d_burst_len << std::endl;
    return d_num_steps*d_burst_len;
}

} /* namespace sfcwRadar */
} /* namespace gr */
