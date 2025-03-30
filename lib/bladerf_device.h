/* -*- c++ -*- */
/*
 * Author: Hui HUANG
 * Email: hui.huang@uni.lu
 *
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef BLADERF_DEVICE_H
#define BLADERF_DEVICE_H

#include <string>
#include <libbladeRF.h> 
#include "misc.h"
#include <volk/volk.h>

/**
 * This class setups the bladeRF 2.0 device as a radar, and provides functions to control the behaviours
 * */
class BladerfDevice {
public:

    /**
     * Class Constructor
     * The Constructor only save the input parameters and initilize TX and RX metadata.
     * To open and initilize the attached device, @see openDevice() and @see enable_rx_channels()
     * @param   buf_config  Configuration of the buffers on the host
     * @param   enable_biastee  Whether biastees of TX (BT-100 power amplifier) and RX (BT-200 LNA) are connected. Note that here only a flag d_enable_biastee is set
     * @param   frequency_plan  Configuration of the SFCW frequency plan, including start frequency, step size and number of steps
     * */
    BladerfDevice(struct libbladeRF_buffer_config *buf_config, bool enable_biastee, struct frequency_plan_config *frequency_plan); 
    
    /**
     * Class destructor
     * close device if it was opened
     * @see closeDevice()
     * */
    ~BladerfDevice(); 

    /**
     * Open bladeRF 2.0 device, if success, set tunning mode to BLADERF_TUNING_MODE_FPGA
     * @return true if bladeRF 2.0 is successfully opened
     * */
    bool openDevice(); // Opens the BladeRF device

    /**
     * Close opened device
     * Set device pointer to nullptr
     * */
    void closeDevice();
    
    /**
     * Configure and enable the RX channels of the bladeRF 2.0 device.
     * Configure the frequency, gain, bandwidth, gain mode and sampling rate of the specified RX channels
     * The function also enable biastee of RX channel for receiving radar echos if d_enable_biastee is set during class construction
     * @note User can enable only one RX channel to receive radar echos by setting ref_rx_config to nullptr
     *
     * @param  ref_rx_config    RX channel configurations for receiving reference signals. Set it to nullptr if no reference RX is required
     * @param   radar_rx_config     RX channel configurations for receiving radar echos
     * return 0 if success
     * */
    int enable_rx_channels(struct channel_config *ref_rx_config, struct channel_config *radar_rx_config);
    
    /**
     * Configure and enable the TX channels of the bladeRF 2.0 device.
     * Configure the frequency, gain, bandwidth and sampling rate of the specified TX channels 
     * The TX channels are configured to use SC16 Q11 samples *with* metadata
     * The biastee of the TX channel for transmitting radar pulses is enabled if d_enable_biastee is set during class construction
     * @note User can enable only one TX channel to transmit radar pulse by setting ref_tx_config to nullptr
     *
     * @param   ref_tx_config   TX channel configurations for transmitting reference signals. Set it to nullptr if no reference TX is required
     * @param   radar_tx_config     TX channel configurations for transmitting radar pulses.
     * @return 0 if success
     * */
    int enable_tx_channels(struct channel_config *ref_tx_config, struct channel_config *radar_tx_config);

    /**
     * Call this function if only on tx is used. The reference signal in this case is feed to the reference RX channel via a directional coupler
     * The frequency, gain, bandwidth and sampling rate of the TX channel are configured as specified
     * The TX channel is configured to use SC16 Q11 samples *with* metadata
     * The biastee of the TX channel for transmitting radar pulses is enabled if d_enable_biastee is set during class construction
     * @param   radar_tx_config     TX channel configurations for transmitting radar pulses.
     * @return 0 if success
     * */
    int enable_single_tx_channel(struct channel_config *radar_tx_config);

    /**
     * Configure and enable TX and RX channels. It essentially call @see enable_rx_channels(), and @see enable_tx_channels() sequentially.
     * ref_tx_config must be provided when using two TX channels, otherwise set ref_tx_config as nullptr (only enable radar TX channel)
     * ref_rx_config must be provided when using two RX channels, otherwise set ref_rx_config as nullptr (only enable radar RX channel)
     * @param   radar_tx_config     TX channel configurations for transmitting radar pulses
     * @param   radar_rx_config     RX channel configurations for receiving radar echos
     * @param   ref_tx_config   TX channel configurations for transmitting reference signals. Set it to nullptr if no reference tx is needed
     * @param   ref_rx_config   RX channel configurations for receiving reference signals. Set it to nullptr if no reference rx is needed
     * @return 0 if success.
     * */
    int enable_channels(struct channel_config *radar_tx_config, struct channel_config *radar_rx_config, struct channel_config *ref_tx_config, struct channel_config *ref_rx_config);
    
    /**
     * set quick tune to provide faster frequency re-tuning.
     * This function gets tuning parameters of TX and RX channels for each frequency step, and store them into d_quick_tunes_tx and d_quick_tunes_rx, respectively.
     * @return 0 if success
     * */
    int set_quick_tune();

    /**
     * Tune RX channels to the specified frequency immediately
     * @param   freq_index  index to specify the tuning frequency. It should be smaller than num_steps as specified by frequency_plan
     * @retune 0 if success
     * @note, call this function only after @see set_quick_tune() is called
     * */
    int tune_rx(int freq_index);
    
    /**
     * Tune TX channels to the specified frequency immediately
     * @param   freq_index  index to specify the tuning frequency. It should be smaller than num_steps as specified by frequency_plan
     * @retune 0 if success
     * @note, call this function only after @see set_quick_tune() is called
     * */
    int tune_tx(int freq_index);
    
    /**
     * Create send and recv threads, schedule transmitting and receiving at the same time stamp
     * @param   d_ts_inc_send   The transmitting will be scheduled d_ts_inc_send ms in the future 
     * @param   d_ts_inc_recv  The receiving will be scheduled d_ts_inc_recv ms in the future 
     * @param   samples_to_send     a pointer of the buffer that stores samples to send
     * @param   num_samples_to_send     number of samples to send
     * @param[out]   rec_buf     a ponter of the buffer to store the received samples
     * @param   num_samples_to_recv     number of samples to receive
     * @return 0 if success
     * */
    int pulse(float d_ts_inc_send, float d_ts_inc_recv, int16_t *samples_to_send, unsigned int num_samples_to_send, int16_t *rec_buf, unsigned int num_samples_to_recv);

    /**
     * Getters
     * */
    struct bladerf* get_device_handler();

    /**
     * setters
     * */
    int set_gain(bladerf_gain gain, bladerf_channel ch);

protected:
    struct bladerf_devinfo dev_info;
    bladerf* device; /**< Pointer to the BladeRF device */
    /**
     * libbladerf buffer setup
     * */
    size_t d_num_buffers = 8;
    size_t d_buffer_size = 2048;
    size_t d_num_transfers = 4;
    const unsigned int timeout_ms = 2000;

    /**
     * Flag to indicate if BT-100 and BT-200 are connected to the TX and RX ports, respectively.
     * */
    bool d_enable_biastee;


    /**
     * variables to save the sfcw frequency plan
     * */
    bladerf_frequency d_start_freq;
    bladerf_frequency d_step_size;
    int d_num_steps = 0;
    
    /**
     * variables to save the quick retune parameters of each frequency step 
     * */
    struct bladerf_quick_tune_info *d_quick_tunes_tx = nullptr;
    struct bladerf_quick_tune_info *d_quick_tunes_rx = nullptr;
    
    /**
     * Tx and Rx metadata
     * */
    struct bladerf_metadata d_rx_meta;
    struct bladerf_metadata d_tx_meta;

    /**
     * Pointers to Tx and Rx buffers
     * */
    int16_t *_16icbuf_in = nullptr;              /**< raw samples to bladeRF */
    unsigned int _16icbuf_in_num_samples;           /**< number of samples in the buffer pointed by _16icbuf_in*/

    int16_t *_16icbuf_out = nullptr;              /**< raw samples from bladeRF */
    unsigned int _16icbuf_out_num_samples;          /**< number of samples to receive*/
    
    /**
     * Setup given channel
     * @param   c   configurations of the specified channel
     * return 0 if the specified channel is set
     * */
    int configure_channel(struct channel_config *c);
    
    /**
     * transmit samples at the timestamp specified by d_tx_meta.timestamp
     * @note before call this function, make sure that _16icbuf_in and _16icbuf_in_num_samples are correctly set
     * */
    void send();

    /**
     * receive samples at the timestamp specified by d_rx_meta.timestamp
     * @note before call this function, make sure that _16icbuf_out and _16icbuf_out_num_samples are correctly set
     * */
    void recv();
};

#endif // BLADERF_DEVICE_H
