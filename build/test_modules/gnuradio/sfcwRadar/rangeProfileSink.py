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
import json

class rangeProfileSink(gr.sync_block):
    """
    docstring for block rangeProfileSink
    """
    def __init__(self, numSteps, dir):
        gr.sync_block.__init__(self,
            name="rangeProfileSink",
            in_sig=[numpy.complex64],
            out_sig=None)
        self.numSteps = numSteps
        self.dir = dir
        self.numScanReceived = 0


    def work(self, input_items, output_items):
        in0 = input_items[0]
        print('input_items len:' + str(len(in0)))
        tagTuple = self.get_tags_in_window(0,0,len(input_items[0]))
        for tag in tagTuple:
            if(pmt.to_python(tag.key) == "c_gps"):
                print("received a new scan")
                gps = pmt.to_python(tag.value)
                print(gps)
                print(type(in0[0]))
                print(in0.shape)
                newScan = {"gps":gps,"rangProfile_real":numpy.real(in0).tolist(),"rangProfile_imag":numpy.imag(in0).tolist()}
                print(newScan)
                with open(self.dir+'/scan_'+str(self.numScanReceived)+'.json','w') as f:
                    json.dump(newScan,f)
                self.numScanReceived = self.numScanReceived + 1

        return len(input_items[0])
