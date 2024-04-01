#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#



from gnuradio import gr
from gnuradio import blocks
from gnuradio import sfcwRadar

class radarTxRxSimulator(gr.hier_block2):
    """
    docstring for block radarTxRxSimulator
    """
    def __init__(self, tune_threshold, start_freq, samp_rate, freq_step, num_steps, tone_freq, ob_range):
        gr.hier_block2.__init__(self,
            "radarTxRxSimulator",
            gr.io_signature.makev(2,2,[gr.sizeof_gr_complex*1,gr.sizeof_gr_complex*1]),  # Input signature
            gr.io_signature.makev(2,2,[gr.sizeof_gr_complex*1,gr.sizeof_gr_complex*1]),  # Input signature
        )

        ### Parameters ###
        self.tune_threshold = tune_threshold
        self.start_freq = start_freq
        self.LO_freq = self.start_freq
        self.samp_rate = samp_rate
        self.num_steps = num_steps
        self.freq_step = freq_step
        self.max_freq = self.start_freq + (freq_step*num_steps)
        self.tone_freq = tone_freq
        self.ob_range = ob_range
        print('starting freq: ', str(self.start_freq))
        print('step_freq: ', str(self.freq_step))
        print('max_freq: ', str(self.max_freq))
        print('ob_range: ', str(self.ob_range))

        ### Blocks ###
        self.blocks_phase_shift_1 = blocks.phase_shift(4*3.1415926*(self.LO_freq+self.tone_freq[1])*self.ob_range/3e8, True)
        self.blocks_phase_shift_0 = blocks.phase_shift(4*3.1415926*(self.LO_freq+self.tone_freq[0])*self.ob_range/3e8, True)
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        
        # tunner block control the frequency stepping
        print('tune_th: ', str(self.tune_threshold))
        self.tunner = sfcwRadar.frequencyTunner(self.tune_threshold,self)
        
        ### Connections ###
        self.connect((self,0),(self.blocks_phase_shift_0,0))
        self.connect((self,1),(self.blocks_phase_shift_1,0))
        self.connect((self.blocks_phase_shift_0,0),(self.blocks_add_xx_0,0))
        self.connect((self.blocks_phase_shift_1,0),(self.blocks_add_xx_0,1))
        self.connect((self.blocks_add_xx_0,0),(self.tunner,0))
        self.connect((self.tunner,0),(self,0))

        self.connect((self,0),(self.blocks_add_xx_0_0,0))
        self.connect((self,1),(self.blocks_add_xx_0_0,1))
        self.connect((self.blocks_add_xx_0_0,0),(self,1))

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self.blocks_phase_shift_0.set_shift(4*3.1415926*(self.LO_freq+self.tone_freq[0])*self.ob_range/3e8)
        self.blocks_phase_shift_1.set_shift(4*3.1415926*(self.LO_freq+self.tone_freq[1])*self.ob_range/3e8) 

    def get_ob_range(self):
        return self.ob_range

    def set_ob_range(self,ob_range):
        print('change ob_range')
        print('new_phase_diff 0: '+str(4*3.1415926*(self.LO_freq+self.tone_freq[0])*self.ob_range/3e8))
        print('new_phase_diff 1: '+str(4*3.1415926*(self.LO_freq+self.tone_freq[1])*self.ob_range/3e8))
        self.ob_range = ob_range
        self.blocks_phase_shift_0.set_shift(4*3.1415926*(self.LO_freq+self.tone_freq[0])*self.ob_range/3e8)
        self.blocks_phase_shift_1.set_shift(4*3.1415926*(self.LO_freq+self.tone_freq[1])*self.ob_range/3e8) 

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
    
    def next_freq(self):
        next_LO_freq = self.LO_freq + self.freq_step
        if next_LO_freq > self.max_freq:
            print('stepping finished, restart from origin')
            print('ob_range: ' + str(self.ob_range))
            next_LO_freq = self.start_freq
        #print("next_LO_freq: ", str(next_LO_freq))
        #self.lock()
        self.set_LO_freq(next_LO_freq)
        #self.unlock() 
