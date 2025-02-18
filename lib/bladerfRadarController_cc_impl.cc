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
                                float ts_inc_recv)
{
    return gnuradio::make_block_sptr<bladerfRadarController_cc_impl>(start_freq,
                                                                     num_steps,
                                                                     step_size,
                                                                     samp_rate,
                                                                     rx_gain,
                                                                     tx_gain,
                                                                     ref_gain,
                                                                     enable_biastee,
                                                                     burst_len,
                                                                     recv_buf_len,
                                                                     num_buffers,
                                                                     buffer_size,
                                                                     num_transfers,
                                                                     cw_amplitude,
                                                                     cw_frequency,
                                                                     isChirp,
                                                                     chirp_bandwidth,
                                                                     ts_inc_send,
                                                                     ts_inc_recv);
}


/*
 * The private constructor
 */
bladerfRadarController_cc_impl::bladerfRadarController_cc_impl(
    bladerf_frequency start_freq,
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
    float ts_inc_recv)
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
    d_step_size = step_size;
    d_num_steps = num_steps;
    d_freq_index = 0;
    d_samp_rate = samp_rate;
    d_tx_gain = tx_gain;
    d_rx_gain = rx_gain;
    d_ref_gain = ref_gain;
    d_enable_biastee = enable_biastee;
    d_burst_len = burst_len;
    std::cout << "burst_len: " << d_burst_len << std::endl;
    d_recv_len = recv_buf_len;
    std::cout << "recv_len: " << d_recv_len << std::endl;

    if(d_recv_len < d_burst_len){
        std::cout << "WARNING: recv_len is smaller than burst_len" << std::endl;
    }

    d_num_buffers = num_buffers;
    d_buffer_size = buffer_size;
    d_num_transfers = num_transfers;

    d_cw_amplitude = cw_amplitude;
    d_cw_frequency = cw_frequency;
    d_isChirp = isChirp;
    d_chirp_bandwidth = chirp_bandwidth;
    d_channel_bandwidth = d_chirp_bandwidth;

    std::cout << "**************************Summary of Radar parameters*************************" << std::endl;
    std::cout << "Start frequency: " << d_start_freq << std::endl;
    std::cout << "Bandiwdth between two consecutive frequency step: " << d_step_size << std::endl;
    std::cout << "Num of steps: " << d_num_steps << std::endl;
    std::cout << "Max frequency: " << d_start_freq + d_step_size * (num_steps-1) << std::endl; 
    std::cout << "Sampling rate: " << samp_rate << std::endl; 
    std::cout << "Is biastee enabled: " << d_enable_biastee << std::endl; 
    std::cout << "Is chirp waveform used:" << d_isChirp << std::endl; 
    
    /**
     * FPGA time steps to wait for transmission after frequency tunning
     * */
    d_ts_inc_rec = (uint64_t)(d_samp_rate * ts_inc_recv)/1000;
    d_ts_inc_send = (uint64_t)(d_samp_rate * ts_inc_send)/1000;
    
    /**
     * Initialize tx and rx metadata
     * */
    memset(&d_rx_meta, 0, sizeof(d_rx_meta));
    memset(&d_tx_meta, 0, sizeof(d_tx_meta));
    d_tx_meta.flags = BLADERF_META_FLAG_TX_BURST_START | BLADERF_META_FLAG_TX_BURST_END; //send as burst
    //std::cout << "d_tx_meta.flags = " << d_tx_meta.flags << std::endl;
    //std::cout << (BLADERF_META_FLAG_TX_BURST_START | BLADERF_META_FLAG_TX_BURST_END) << std::endl;

    /* Set up constraints */
    int const alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
    set_alignment(std::max(1,alignment_multiple)); 
    
    /* Allocate memory for conversions in work() */
    size_t alignment = volk_get_alignment();
    /**
     * Bladerf accept int16_t as input and output samples in int16_t while gnuradio use 2x float to store one sample 
     * */
    //Because we use two TXs, the input samples are interleaved so the size of buffer for sending should be twice as the d_burst_len
    _32fcbuf_in = reinterpret_cast<gr_complex *>(volk_malloc(2*d_burst_len*sizeof(gr_complex), alignment));
    //_16icbuf_in needs to be twice as the size of _32fcbuf_in
    _16icbuf_in = reinterpret_cast<int16_t *>(volk_malloc(2*2*d_burst_len*sizeof(int16_t), alignment));

    //Because we use two RXs, the output samples are interleaved so the size of buffer for receiving should be twice as the d_recv_len
    _32fcbuf_out = reinterpret_cast<gr_complex *>(volk_malloc(2*d_recv_len*sizeof(gr_complex), alignment));
    //_16icbuf_out need to be twice as the size of _32fcbuf_out
    _16icbuf_out = reinterpret_cast<int16_t *>(volk_malloc(2*2*d_recv_len*sizeof(int16_t), alignment));

    int status = init_device();
    /**
     * Set input/ouput contrains based on the d_recv_len
     * */
    // two RXs
    set_output_multiple(2);
    set_min_noutput_items(d_recv_len*num_steps);
    set_min_output_buffer(d_recv_len*num_steps*2);

}


int bladerfRadarController_cc_impl::init_device(){

    std::cout << "*************************Initialize device************************" <<std::endl;
    d_scan = false;
    d_continuous_scan_flag = false;

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
        //bladerf_set_tuning_mode(dev, BLADERF_TUNING_MODE_FPGA);
        bladerf_set_tuning_mode(dev, BLADERF_TUNING_MODE_HOST);
        bladerf_tuning_mode current_mode;
        bladerf_get_tuning_mode(dev, &current_mode);
        std::cout << "Tunning mode is: " << current_mode << std::endl;
        
        /**
         * Configure RX channel 0. 
         * RX channel 1 is used for receiving echo signals
         * */
        config.channel = RADAR_RX;
        config.frequency = d_start_freq;
        config.bandwidth = d_chirp_bandwidth;//d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_rx_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "Channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        
        /**
         * Configure RX channel 1
         * This channel is used for receiving ref signal 
         * */
        config.channel = REF_RX;
        config.frequency = d_start_freq;
        config.bandwidth = d_channel_bandwidth;//d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_ref_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "Channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        /**
         * Configure TX channel 0
         * This channel is used for sending radar signal 
         * */
        config.channel = RADAR_TX;
        config.frequency = d_start_freq;
        config.bandwidth = d_chirp_bandwidth;//d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_tx_gain;
        status = configure_channel(dev, &config);
        if (status !=0){
            std::cerr << "Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "Channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        /**
         * Configure TX channel 1
         * This channel is used for sending ref signal 
         * */
        config.channel = REF_TX;
        config.frequency = d_start_freq;
        config.bandwidth = d_chirp_bandwidth;//d_samp_rate/2;
        config.samplerate = d_samp_rate;
        config.gain = d_ref_gain;
        status = configure_channel(dev,&config);
        if (status !=0){
            std::cerr << "Channel " << config.channel << ": configure_channel failed" << std::endl;
        }else{
            std::cout << "Channel " << config.channel << ": configure_channel succed" << std::endl;
        }
        
        /* Initialize synchronous interface on RXs and TXs */
        status = init_sync(dev);
        if (status != 0) {
            fprintf(stderr, "Failed to init sync interface: %s\n", bladerf_strerror(status));
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

    /**
     * Set gain
     * */
    std::cout << "Set channel " << c->channel << " gain to "<< c->gain << std::endl;
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
                                 BLADERF_FORMAT_SC16_Q11_META, d_num_buffers, 
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
                                 BLADERF_FORMAT_SC16_Q11_META, d_num_buffers,
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
     * Set bias tee for RADAR_TX
     * */
    status = bladerf_set_bias_tee(dev, RADAR_TX, d_enable_biastee);
    if(status != 0){
        std::cerr << "Set channel: " << RADAR_TX << " bias tee failed" << std::endl;
    }else{
        bool is_bias_tee_enabled = false;
        status = bladerf_get_bias_tee(dev, RADAR_TX, &is_bias_tee_enabled);
        std::cout << "bias tee status of chennel " << RADAR_TX << " :" << is_bias_tee_enabled << std::endl;
    }
    
    /**
     * Set bias tee of RADAR_RX
     * */
    status = bladerf_set_bias_tee(dev, RADAR_RX, d_enable_biastee);
    if(status != 0){
        std::cerr << "Set channel: " << RADAR_RX << " bias tee failed" << std::endl;
    }else{
        bool is_bias_tee_enabled = false;
        status = bladerf_get_bias_tee(dev,RADAR_RX, &is_bias_tee_enabled);
        std::cout << "bias tee status of chennel " << RADAR_RX << " :" << is_bias_tee_enabled << std::endl;
    }
    
    /**
     * Set AGC of RADAR_RX
     * */
    status = bladerf_set_gain_mode(dev, RADAR_RX, BLADERF_GAIN_MANUAL);
    //status = bladerf_set_gain_mode(dev, RADAR_RX, BLADERF_GAIN_HYBRID_AGC);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode = %u: %s\n",RADAR_RX,
        bladerf_strerror(status));
        return status;
    }
    
    bladerf_gain_mode current_gain_mode;
    status = bladerf_get_gain_mode(dev, RADAR_RX, &current_gain_mode);
    if(status!=0){
        std::cerr << "Falied to read gain mode from channel: " << RADAR_RX << std::endl;
    }else{
        std::cout << "Channel: " << RADAR_RX << ", gain mode: " << current_gain_mode << std::endl;
    } 
    
    /**
     * Set AGC for REF_RX
     * */
    //status = bladerf_set_gain_mode(dev, REF_RX, BLADERF_GAIN_MANUAL);
    status = bladerf_set_gain_mode(dev, REF_RX, BLADERF_GAIN_HYBRID_AGC);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain mode = %u: %s\n", REF_RX,
        bladerf_strerror(status));
        return status;
    }

    status = bladerf_get_gain_mode(dev, REF_RX, &current_gain_mode);
    if(status!=0){
        std::cerr << "Falied to read gain mode from channel: " << REF_RX << std::endl;
    }else{
        std::cout << "Channel: " << REF_RX << ", gain mode: " << current_gain_mode << std::endl;
    }

    status = bladerf_enable_module(dev, RADAR_RX, true);
    if (status != 0) {
        std::cerr << "RADAR_RX enable failed" << std::endl;
        return status;
    }else{
        std::cout << "RADAR_RX enalbed" << std::endl;
    }
    status = bladerf_enable_module(dev, REF_RX, true);
    if (status != 0) {
        std::cerr << "REF_RX enable failed" << std::endl;
        return status;
    }else{
        std::cout << "REF_RX enalbed" << std::endl;
    }
    status = bladerf_enable_module(dev, RADAR_TX, true);
    if (status != 0) {
        std::cerr << "RADAR_TX enable failed" << std::endl;
        return status;
    }else{
        std::cout << "RADAR_TX enalbed" << std::endl;
    } 
    status = bladerf_enable_module(dev, REF_TX, true);
    if (status != 0) {
        std::cerr << "REF_TX enable failed" << std::endl;
        return status;
    }else{
        std::cout << "REF_TX enalbed" << std::endl;
    } 
    
    /**
     * varify if the gains of each channel is correctly assigned
     * */
    bladerf_gain current_gain;
    status = bladerf_get_gain(dev,RADAR_RX,&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << RADAR_RX << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << RADAR_RX << ", gain: " << current_gain << std::endl;
    }
    
    status = bladerf_get_gain(dev,REF_RX,&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << REF_RX << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << REF_RX << ", gain: " << current_gain << std::endl;
    }
    
    status = bladerf_get_gain(dev,RADAR_TX,&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << RADAR_TX << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << RADAR_TX << ", gain: " << current_gain << std::endl;
    }
    
    status = bladerf_get_gain(dev,REF_TX,&current_gain);
    if(status !=0){
        std::cerr << "failed to get gain for channel" << REF_TX << std::endl;
        return status;
    }else{
        std::cout << "Chennel" << REF_TX << ", gain: " << current_gain << std::endl;
    }

    return status;
}

int bladerfRadarController_cc_impl::set_quick_tune(){
    int status;
    bladerf_frequency freq;
    freq = d_start_freq;
    for (int i = 0; i < d_num_steps; i++){
        //std::cout << "set quick tune parameters for frequency: " << freq << std::endl;
        status = bladerf_set_frequency(dev, BLADERF_TX, freq);
        if(status!=0){
            std::cerr << "set TX frequency to: "<< freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_tx[i].freq = freq;
        status = bladerf_get_quick_tune(dev, BLADERF_TX, &d_quick_tunes_tx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for TX" << std::endl;
            return status;
        }
        
        status = bladerf_set_frequency(dev, BLADERF_RX, freq);
        if(status!=0){
            std::cerr << "set RX frequency to: "<< freq << " failed" << std::endl;
            return status;
        }
        d_quick_tunes_rx[i].freq = freq;
        status = bladerf_get_quick_tune(dev, BLADERF_RX, &d_quick_tunes_rx[i].quick_tune);
        if(status != 0){
            std::cerr << "failed to get quick tune for RX" << std::endl;
            return status;
        }
        freq = freq + d_step_size;
    }

    d_freq_index = 0;
    return status;
}

int bladerfRadarController_cc_impl::wait_for_timestamp(struct bladerf *dev, bladerf_direction dir, uint64_t timestamp, unsigned int timeout_ms){
    //std::cout<<"wait for timestamp: " << timestamp << std::endl;
    int status;
    uint64_t curr_ts = 0;
    unsigned int slept_ms = 0;
    bool done;
    do{
        status = bladerf_get_timestamp(dev, dir, &curr_ts);
        //std::cout << "curr_ts: " << curr_ts << std::endl;
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

int bladerfRadarController_cc_impl::set_tx_gain(bladerf_gain tx_gain){
    std::cout << "set radar tx gain to: " << tx_gain << std::endl;
    d_tx_gain = tx_gain;
    int status = bladerf_set_gain(dev,RADAR_TX,d_tx_gain);
    return status;
}

int bladerfRadarController_cc_impl::set_rx_gain(bladerf_gain rx_gain){
    d_rx_gain = rx_gain;
    int status = bladerf_set_gain(dev, RADAR_RX, d_rx_gain);
    return status;
}

int bladerfRadarController_cc_impl::set_ref_gain(bladerf_gain ref_gain){
    d_ref_gain = ref_gain;
    int status = bladerf_set_gain(dev, REF_TX, d_ref_gain);
    return status;
}

int bladerfRadarController_cc_impl::set_chirp_bandwidth(float chirp_bandwidth){
    d_chirp_bandwidth = chirp_bandwidth;
    return 0;
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

void bladerfRadarController_cc_impl::generate_chirp_samples(){
    float phase = 0;
    float f_inst = -d_chirp_bandwidth/2;
    float dt = 1/(float)d_samp_rate;
    int _32fcbuf_in_index = 0;
    memset(_32fcbuf_in,0,d_burst_len*2*sizeof(gr_complex));
    for (size_t i=0; i<d_burst_len;i++){
        f_inst = -d_chirp_bandwidth/2 + d_chirp_bandwidth*i/(d_burst_len);
        phase = phase + 2 * M_PI * f_inst * dt;
        _32fcbuf_in[_32fcbuf_in_index] = d_cw_amplitude * std::exp(std::complex<float>(0,phase));
        _32fcbuf_in[_32fcbuf_in_index+1] = _32fcbuf_in[_32fcbuf_in_index];
        _32fcbuf_in_index = _32fcbuf_in_index+2;
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
    status = bladerf_sync_tx(dev, static_cast<void const *>(_16icbuf_in), d_burst_len*2, &d_tx_meta, timeout_ms); 

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
    status = bladerf_sync_rx(dev, static_cast<void *>(_16icbuf_out), d_recv_len*2, &d_rx_meta, timeout_ms);

    if (status != 0){
        std::cerr << "receiving failed: " << bladerf_strerror(status) << std::endl;
    }else if (d_rx_meta.status & BLADERF_META_STATUS_OVERRUN){
       std::cerr << "Overrun detected in scheduled RX. Number of samples read is: " << d_rx_meta.actual_count << std::endl;
    }
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

    /*if(d_freq_index == 20){
        //std::cout << "increase gain" << std::endl;
        //bladerf_set_gain(dev, RADAR_TX,d_tx_gain+10);
        //bladerf_set_gain(dev, REF_TX,d_ref_gain+10);
    }else if(d_freq_index == 80){
        std::cout << "increase gain again" << std::endl;
        bladerf_set_gain(dev, RADAR_TX,d_tx_gain+30);
        
    }else if(d_freq_index == 0){
        std::cout << "tune gain back" << std::endl;
        bladerf_set_gain(dev,RADAR_TX,d_tx_gain);
        //bladerf_set_gain(dev,REF_TX,d_ref_gain);
    }*/

    //std::cout<<"tunning rx to: " << d_quick_tunes_rx[index].freq << std::endl;
    int status = bladerf_schedule_retune(dev, BLADERF_RX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_rx[d_freq_index].quick_tune);
    if(status != 0){
        std::cerr << "failed to tune RX: " << bladerf_strerror(status) << std::endl;
        return status;
    }

    //std::cout<<"tunning tx to: " << d_quick_tunes_tx[index].freq << std::endl;
    //std::chrono::steady_clock::time_point tune_begin = std::chrono::steady_clock::now();
    status = bladerf_schedule_retune(dev, BLADERF_TX, BLADERF_RETUNE_NOW, 0, &d_quick_tunes_tx[d_freq_index].quick_tune);
    //std::chrono::steady_clock::time_point tune_end = std::chrono::steady_clock::now();
    //std::cout << "Time used for tuning = " << std::chrono::duration_cast<std::chrono::microseconds>(tune_end - tune_begin).count() << "[µs]" << std::endl;
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
    /**
     * Pointer to output
     * */
    gr_complex **out = reinterpret_cast<gr_complex **>(&output_items[0]);
    /**
     * Make sure the flags of tx and rx are correct
     * */
    d_tx_meta.flags = BLADERF_META_FLAG_TX_BURST_START | BLADERF_META_FLAG_TX_BURST_END;
    d_rx_meta.flags = 0;
    if(d_scan == true){
        std::cout << "scanning..." << std::endl;
        begin = std::chrono::steady_clock::now();
        //add a new scan tag
        pmt::pmt_t new_scan_tag_key = pmt::string_to_symbol("newScan");
        pmt::pmt_t new_scan_tag_value = pmt::PMT_T;
        add_item_tag(0,nitems_written(0),new_scan_tag_key,new_scan_tag_value);

        //create newFreq tag
        pmt::pmt_t new_freq_tag_key = pmt::string_to_symbol("newFreq");
        // scan cmd received, start sweeping the bandwidth
        for (int i = 0; i < d_num_steps; i++){
            //add a new freq tag
            pmt::pmt_t new_freq_tag_value = pmt::from_uint64(i);
            add_item_tag(0,nitems_written(0)+i*d_recv_len,new_freq_tag_key,new_freq_tag_value);
            
            /**
             * Tune frequency to the next step
             * */
            d_freq_index = i;
            quick_tune();
            
            /**
             * Generate pulse samples, the generated samples for two TXs are stored in _32fcbuf_in
             * */
            if (d_isChirp){
                //Chirp pulse
                generate_chirp_samples();
            }else{
                //Sine pulse
                generate_cw_samples();
            }
            /** 
             * convert floating point to fixed point and scale
             * input_items is gr_complex (2x float), for 2 TXs, so num_points is 2*2*d_burst_len
             * */
            volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
                            SCALING_FACTOR, 2*2*d_burst_len);
            /**
            * create sending and receiving threads
            * */
            int status = bladerf_get_timestamp(dev, BLADERF_TX, &d_tx_meta.timestamp);
            if (status != 0) {
                fprintf(stderr, "Failed to get current TX timestamp: %s\n", bladerf_strerror(status));
            }
            //schedule tx and tx in the future
            d_tx_meta.timestamp += d_ts_inc_send;
            d_rx_meta.timestamp = d_tx_meta.timestamp + d_ts_inc_rec;
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
            // output_items is gr_complex (2x float), receiving from 2 RXs, so num_points is 2*2*d_recv_len
            volk_16i_s32f_convert_32f(reinterpret_cast<float *>(_32fcbuf_out), _16icbuf_out,
                            SCALING_FACTOR, 2*2*d_recv_len);

            //std::cout << "copy the samples into output_items" <<std::endl;
            // we need to deinterleave the multiplex as we copy
            gr_complex const *deint_in = _32fcbuf_out;
            //gr_complex const *deint_in = _32fcbuf_in;

            //std::cout << "deinterleave" << std::endl;
            for (size_t i = 0; i < (d_recv_len); ++i) {
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
    return d_num_steps*d_recv_len;
}

} /* namespace sfcwRadar */
} /* namespace gr */
