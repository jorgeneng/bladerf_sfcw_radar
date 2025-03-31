/* -*- c++ -*- */
/*
 * Copyright 2025 snt.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "sfcw_radar_miso_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>
#include <gnuradio/math.h>
#include "misc.h"
#include "bladerf_device.h"


namespace gr {
namespace sfcwRadar {

using output_type = gr_complex;
sfcw_radar_miso_cc::sptr sfcw_radar_miso_cc::make(bladerf_frequency start_freq,
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
                                                  float ts_inc_send)
{
    return gnuradio::make_block_sptr<sfcw_radar_miso_cc_impl>(start_freq,
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
                                                              pulse_amplitude,
                                                              cw_frequency,
                                                              isChirp,
                                                              chirp_bandwidth,
                                                              ts_inc_send);
}


/*
 * The private constructor
 */
sfcw_radar_miso_cc_impl::sfcw_radar_miso_cc_impl(bladerf_frequency start_freq,
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
                                                 float ts_inc_send)
    : gr::sync_block("sfcw_radar_miso_cc",
                     gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(
                         NUM_RX_CHANNELS /* min outputs */, NUM_RX_CHANNELS /*max outputs */, sizeof(output_type)))
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
    d_samp_rate = samp_rate;
    d_burst_len = burst_len;
    d_num_steps = num_steps;
    d_recv_len = recv_buf_len;

    if(d_recv_len < d_burst_len){
        std::cout << "WARNING: recv_len is smaller than burst_len" << std::endl;
    }

    d_pulse_amplitude = pulse_amplitude;
    d_cw_frequency = cw_frequency;
    d_isChirp = isChirp;
    d_chirp_bandwidth = chirp_bandwidth;

    std::cout << "**************************Summary of Radar parameters*************************" << std::endl;
    std::cout << "Start frequency: " << start_freq << std::endl;
    std::cout << "Bandiwdth between two consecutive frequency step: " << step_size << std::endl;
    std::cout << "Num of steps: " << num_steps << std::endl;
    std::cout << "Max frequency: " << start_freq + step_size * (num_steps-1) << std::endl; 
    std::cout << "Sampling rate: " << samp_rate << std::endl; 
    std::cout << "burst_len: " << d_burst_len << std::endl;
    std::cout << "recv_len: " << d_recv_len << std::endl;
    std::cout << "Is biastee enabled: " << enable_biastee << std::endl; 
    std::cout << "Is chirp waveform used:" << d_isChirp << std::endl; 
    
    /**
     * FPGA time steps to wait for transmission after frequency tunning
     * */
    d_ts_inc_send = (uint64_t)(d_samp_rate * ts_inc_send)/1000;
    
    init_sample_buffers();
    
    /**
     * Set input/ouput contrains based on the d_recv_len
     * */
    //two rxs
    set_output_multiple(NUM_RX_CHANNELS);
    set_min_noutput_items(d_recv_len*num_steps);
    set_min_output_buffer(d_recv_len*num_steps*NUM_RX_CHANNELS);
    
    /**
     * Initialize device
     */ 
    std::cout << "*************************Initialize device************************" <<std::endl;
    d_scan = false;
    d_continuous_scan_flag = false;

    bladeRF= new BladerfDevice();

    if(bladeRF->openDevice()){
        int status = 0;
        //device opened, configure tx and rx channels
        struct channel_config radar_tx_config;
        radar_tx_config.channel = RADAR_TX;
        radar_tx_config.frequency = start_freq;
        radar_tx_config.bandwidth = d_samp_rate/2;
        radar_tx_config.samplerate = d_samp_rate;
        radar_tx_config.gain = tx_gain;

        struct channel_config radar_rx_config = radar_tx_config;
        radar_rx_config.channel = RADAR_RX;
        radar_rx_config.gain = rx_gain;
        //radar_rx_config.gain_mode = BLADERF_GAIN_AUTOMATIC;

        struct channel_config ref_rx_config = radar_tx_config;
        ref_rx_config.channel = REF_RX;
        ref_rx_config.gain = ref_gain;
        //ref_rx_config.gain_mode = BLADERF_GAIN_AUTOMATIC;
    
        usb_buffer_config buf_config;
        buf_config.num_buffers = num_buffers;
        buf_config.buffer_size = buffer_size;
        buf_config.num_transfers = num_transfers;
        status = bladeRF->enable_channels(&radar_tx_config, &radar_rx_config, nullptr, &ref_rx_config, &buf_config, enable_biastee);
        if(status!=0){
            std::cerr << "Failed to enable rx channels" << std::endl;
            bladeRF->closeDevice();
            return;
        }

        //tx and rx channels all enabled, set quick tune
        frequency_plan_config frequency_plan;
        frequency_plan.start_freq = start_freq;
        frequency_plan.num_steps = num_steps;
        frequency_plan.step_size = step_size;
        
        status = bladeRF->set_quick_tune(&frequency_plan);
        if(status!=0){
            std::cerr << "Set quick tune failed" << std::endl;
            bladeRF->closeDevice();
            return;
        }
        std::cout << "Device initialisation completed" << std::endl;
    }else{
        std::cerr << "Failed to open device" << std::endl;
    }
}

void sfcw_radar_miso_cc_impl::init_sample_buffers(){
    /* Set up constraints */
    int const alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
    set_alignment(std::max(1,alignment_multiple)); 
    
    /* Allocate memory for conversions in work() */
    size_t alignment = volk_get_alignment();
    /**
     * Bladerf accept int16_t as input and output samples in int16_t while gnuradio use 2x float to store one sample 
     * */
    _32fcbuf_in = reinterpret_cast<gr_complex *>(volk_malloc(NUM_TX_CHANNELS*d_burst_len*sizeof(gr_complex), alignment));
    _16icbuf_in = reinterpret_cast<int16_t *>(volk_malloc(2*NUM_TX_CHANNELS*d_burst_len*sizeof(int16_t), alignment));

    _32fcbuf_out = reinterpret_cast<gr_complex *>(volk_malloc(NUM_RX_CHANNELS*d_recv_len*sizeof(gr_complex), alignment));
    _16icbuf_out = reinterpret_cast<int16_t *>(volk_malloc(2*NUM_RX_CHANNELS*d_recv_len*sizeof(int16_t), alignment));
}

void sfcw_radar_miso_cc_impl::generate_cw_samples(){
    memset(_32fcbuf_in,0,d_burst_len*NUM_TX_CHANNELS*sizeof(gr_complex));
    for (size_t i=0;i<d_burst_len*NUM_TX_CHANNELS;i++){
        _32fcbuf_in[i] += d_pulse_amplitude*exp(d_phase);
        d_phase = gr_complex(0,std::fmod(imag(d_phase) + 2 * GR_M_PI * d_cw_frequency / (float)d_samp_rate,2*GR_M_PI));
    }
}

void sfcw_radar_miso_cc_impl::generate_chirp_samples(){
    float phase = 0;
    float f_inst = -d_chirp_bandwidth/2;
    float dt = 1/(float)d_samp_rate;
    int _32fcbuf_in_index = 0;
    memset(_32fcbuf_in,0,d_burst_len*NUM_TX_CHANNELS*sizeof(gr_complex));
    for (size_t i=0; i<d_burst_len;i++){
        f_inst = -d_chirp_bandwidth/2 + d_chirp_bandwidth*i/(d_burst_len);
        phase = phase + 2 * M_PI * f_inst * dt;
        _32fcbuf_in[_32fcbuf_in_index] = d_pulse_amplitude * std::exp(std::complex<float>(0,phase));
        _32fcbuf_in_index = _32fcbuf_in_index+1;
    }
}

void sfcw_radar_miso_cc_impl::handle_scan_msg(const pmt::pmt_t& msg){
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

/*
 * Our virtual destructor.
 */
sfcw_radar_miso_cc_impl::~sfcw_radar_miso_cc_impl() {
    volk_free(_16icbuf_in);
    volk_free(_16icbuf_out);
    volk_free(_32fcbuf_in);
    volk_free(_32fcbuf_out);
    _16icbuf_in = NULL;
    _16icbuf_out = NULL;
    _32fcbuf_in = NULL;
    _32fcbuf_out = NULL;
}

int sfcw_radar_miso_cc_impl::work(int noutput_items,
                                  gr_vector_const_void_star& input_items,
                                  gr_vector_void_star& output_items)
{
    /**
     * Pointer to output
     * */
    gr_complex **out = reinterpret_cast<gr_complex **>(&output_items[0]);

    if(d_scan == true){
        std::cout << "scanning..." << std::endl;
        begin = std::chrono::steady_clock::now();
        //add a new scan tag
        pmt::pmt_t new_scan_tag_key = pmt::string_to_symbol("newScan");
        pmt::pmt_t new_scan_tag_value = pmt::PMT_T;
        add_item_tag(0,nitems_written(0),new_scan_tag_key,new_scan_tag_value);

        //create step tag
        pmt::pmt_t new_freq_tag_key = pmt::string_to_symbol("step");
        // scan cmd received, start sweeping the bandwidth
        for (int i = 0; i < d_num_steps; i++){
            //add a step tag
            pmt::pmt_t new_freq_tag_value = pmt::from_uint64(i);
            add_item_tag(0,nitems_written(0)+i*d_recv_len,new_freq_tag_key,new_freq_tag_value);
            
            /**
             * Tune frequency to the next step
             * */
            bladeRF->tune_tx(i);
            bladeRF->tune_rx(i);
            
            /**
             * Generate pulse samples, the generated samples for two TXs are stored in _32fcbuf_in
             * */
            if (d_isChirp){
                //Chirp pulse
                generate_chirp_samples();
            }else{
                //Single tone pulse
                generate_cw_samples();
            }
            /** 
             * convert floating point to fixed point and scale
             * input_items is gr_complex (2x float), for 2 TXs, so num_points is 2*2*d_burst_len
             * */
            volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
                            SCALING_FACTOR, 2*NUM_TX_CHANNELS*d_burst_len);
            
            /**
             * Send a pulse and receive the echo
             * */
            //bladeRF->pulse(d_ts_inc_send, d_ts_inc_send, _16icbuf_in, d_burst_len*NUM_TX_CHANNELS, _16icbuf_out, d_recv_len*NUM_RX_CHANNELS);

            /**
            * process received samples
            * */
            volk_16i_s32f_convert_32f(reinterpret_cast<float *>(_32fcbuf_out), _16icbuf_out,
                            SCALING_FACTOR, 2*NUM_RX_CHANNELS*d_recv_len);

            // we need to deinterleave the multiplex as we copy
            gr_complex const *deint_in = _32fcbuf_out;
            //gr_complex const *deint_in = _32fcbuf_in;

            //std::cout << "deinterleave" << std::endl;
            for (size_t i = 0; i < (d_recv_len); ++i) {
                for (size_t n = 0; n < NUM_RX_CHANNELS; ++n) {
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
    return d_num_steps*d_recv_len;
}

int sfcw_radar_miso_cc_impl::set_radar_tx_gain(bladerf_gain gain){
    int status = bladeRF->set_gain(gain, RADAR_TX);
    return status;
}

int sfcw_radar_miso_cc_impl::set_radar_rx_gain(bladerf_gain gain){
    int status = bladeRF->set_gain(gain, RADAR_RX);
    return status;
}

int sfcw_radar_miso_cc_impl::set_ref_rx_gain(bladerf_gain gain){
    int status = bladeRF->set_gain(gain, REF_RX);
    return status;
}

} /* namespace sfcwRadar */
} /* namespace gr */
