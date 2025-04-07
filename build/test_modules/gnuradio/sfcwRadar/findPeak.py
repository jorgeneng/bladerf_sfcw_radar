#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class findPeak(gr.sync_block):
    """
    docstring for block findPeak
    """
    def __init__(self, mf_size):
        gr.sync_block.__init__(self,
            name="findPeak",
            in_sig=[(np.complex64, mf_size)],
            out_sig=[(np.complex64, 1)],
        )

        self.mf_size = mf_size;


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        #print(len(in0));
        for i in range(len(in0)):
            index = np.argmax(np.abs(in0[i][:]))
            #print(index)
            out[i] = in0[i][index]
        return len(output_items[0])
