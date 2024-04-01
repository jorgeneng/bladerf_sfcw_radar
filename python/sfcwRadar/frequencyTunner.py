#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
from gnuradio import gr
import pmt

class frequencyTunner(gr.sync_block):
    """
    docstring for block frequencyTunner
    """
    def __init__(self, tune_th, radar_transceiver):
        gr.sync_block.__init__(self,
            name="frequencyTunner",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        self.tune_th = tune_th
        self.radar_transceiver = radar_transceiver
        self.stepCmdPortName = 'stepCmd'
        self.message_port_register_in(pmt.intern(self.stepCmdPortName))
        self.set_msg_handler(pmt.intern(self.stepCmdPortName),self.handle_msg)
        self.counter = 0
        
    def work(self, input_items, output_items):
        #in0 = input_items[0]
        #out = output_items[0]
        if self.nitems_written(0) == 0:

            key = pmt.intern('burst')
            value_true = pmt.from_bool(True)
            tag_index_true = self.nitems_written(0)
            self.add_item_tag(0,tag_index_true,key,value_true)
 

        if self.counter >= self.tune_th:
            #print('reach limit, tune transceiver to the next LO freq: ', str(self.counter))
            self.counter = 0
            key = pmt.intern('burst')
            value_true = pmt.from_bool(True)
            value_false = pmt.from_bool(False)
            tag_index_false = self.nitems_written(0) 
            tag_index_true = self.nitems_written(0) + len(input_items[0])
            #print('tag_index: ', str(tag_index_false),'/',str(tag_index_true))
            try:
                self.radar_transceiver.next_freq()
                #self.add_item_tag(0,tag_index_false,key,value_false)
                self.add_item_tag(0,tag_index_true,key,value_true)
            except:
                print('radar_transceiver does not have next_freq method') 
        output_items[0][:] = input_items[0]
        self.counter = self.counter + len(output_items[0])
        return len(output_items[0])

    def handle_msg(self,msg):
        print('received a msg')
        print('samples received in current frequency: ', str(self.counter))
        self.counter = 0
        try:
            self.radar_transceiver.next_freq()
        except:
            print('radar_transceiver does not have next_freq method')
            pass

        return 0

