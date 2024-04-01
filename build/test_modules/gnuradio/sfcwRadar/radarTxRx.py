#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#



from gnuradio import gr
from gnuradio import sfcwRadar
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
import osmosdr
import time

class radarTxRx(gr.hier_block2):
    def __init__(self, tune_threshold, start_freq = 1e9, rx_gain=30, samp_rate=0, tx_gain=30, freq_step = 40e6, num_steps = 10):
        gr.hier_block2.__init__(
            self, "radarTxRx",
                gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
                gr.io_signature.makev(2, 2, [gr.sizeof_gr_complex*1, gr.sizeof_gr_complex*1]),
        )

        ##################################################
        # Parameters
        ##################################################
        self.tune_threshold = tune_threshold
        self.start_freq = start_freq
        self.LO_freq = self.start_freq
        self.rx_gain = rx_gain
        self.samp_rate = samp_rate
        self.tx_gain = tx_gain
        self.num_steps = num_steps
        self.freq_step = freq_step
        self.max_freq = self.start_freq + (freq_step * num_steps)
        print('starting freq: ', str(self.start_freq))
        print('step_freq: ', str(self.freq_step))
        print('max_freq: ', str(self.max_freq))

        ##################################################
        # Blocks
        ##################################################

        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(2) + " " + "bladerf=0,fpga-reload=1,loopback=none,nchan=2,biastee=1"
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(self.LO_freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(rx_gain, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('RX1', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.osmosdr_source_0.set_center_freq(self.LO_freq, 1)
        self.osmosdr_source_0.set_freq_corr(0, 1)
        self.osmosdr_source_0.set_dc_offset_mode(0, 1)
        self.osmosdr_source_0.set_iq_balance_mode(0, 1)
        self.osmosdr_source_0.set_gain_mode(False, 1)
        self.osmosdr_source_0.set_gain(0, 1)
        self.osmosdr_source_0.set_if_gain(20, 1)
        self.osmosdr_source_0.set_bb_gain(20, 1)
        self.osmosdr_source_0.set_antenna('RX2', 1)
        self.osmosdr_source_0.set_bandwidth(0,1)
        

        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + "bladerf=0,fpga-reload=1,loopback=none,nchan=1,biastee=0"
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(self.LO_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(tx_gain, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        # tunner block control the frequency stepping
        print('tune_th: ', str(self.tune_threshold))
        self.tunner = sfcwRadar.frequencyTunner(self.tune_threshold,self)
        
        ##################################################
        # Connections
        ##################################################
        #self.connect((self.osmosdr_source_0, 0), (self, 0))
        self.connect((self.osmosdr_source_0, 0), (self.tunner, 0))
        self.connect((self.osmosdr_source_0, 1), (self, 1))
        self.connect((self.tunner, 0), (self, 0))
        self.connect((self, 0), (self.osmosdr_sink_0, 0))

        ########################################################
        # Message port
        ########################################################
        
        self.msgPortName = 'msgPort'
        self.message_port_register_hier_in(self.msgPortName) 
        self.msg_connect((self, 'msgPort'),(self.tunner,'stepCmd')) 

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        #self.osmosdr_sink_0.stop()
        #self.osmosdr_source_0.stop()
        self.osmosdr_sink_0.set_center_freq(self.LO_freq, 0)
        self.osmosdr_source_0.set_center_freq(self.LO_freq, 0)
        #self.osmosdr_sink_0.start()
        #self.osmosdr_source_0.start()

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        print('set_rx_gain')
        self.rx_gain = rx_gain
        self.osmosdr_source_0.set_gain(self.rx_gain, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.osmosdr_sink_0.set_bandwidth(self.samp_rate, 0)
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0.set_bandwidth(self.samp_rate, 0)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        print('set_tx_gain')
        self.tx_gain = tx_gain
        self.osmosdr_sink_0.set_gain(self.tx_gain, 0)
    
    def next_freq(self):
        next_LO_freq = self.LO_freq + self.freq_step
        if next_LO_freq > self.max_freq:
            print('stepping finished, restart from origin')
            next_LO_freq = self.start_freq
        #print("next_LO_freq: ", str(next_LO_freq))
        #self.lock()
        self.set_LO_freq(next_LO_freq)
        #self.unlock()

