#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import json

class rawSamplesSink(gr.sync_block):
    """
    docstring for block rawSamplesSink
    """
    def __init__(self, file_prefix, start_freq, num_steps, samp_rate, rx_gain, tx_gain, ref_gain, enable_biastee, burst_len, recv_buf_len, cw_amplitude, cw_frequency, isChirp, chirp_bandwidth):
        gr.sync_block.__init__(self,
            name="rawSamplesSink",
            in_sig=[(np.complex64, recv_buf_len*num_steps), (np.complex64, recv_buf_len*num_steps)],
            out_sig=None)

        self.file_prefix = file_prefix
        self.scan_index = 0
        self.scan_param = {
            "start_freq":start_freq,
            "num_steps":num_steps,
            "samp_rate":samp_rate,
            "rx_gain":rx_gain,
            "tx_gain":tx_gain,
            "ref_gain":ref_gain,
            "enable_biastee":enable_biastee,
            "burst_len":burst_len,
            "recv_buf_len":recv_buf_len,
            "cw_amplitude":cw_amplitude,
            "cw_frequency":cw_frequency,
            "isChirp":isChirp,
            "chirp_bandwidth":chirp_bandwidth
        }

        filename = "{}_meta.json".format(file_prefix)
        with open(filename,"w") as f:
            json.dump(self.scan_param, f)
        print("scan parameters: ", self.scan_param)
        print("saved to ", filename)

    def set_file_prefix(self,file_prefix):
        self.file_prefix = file_prefix
        filename = "{}_meta.json".format(file_prefix)
        with open(filename,"w") as f:
            json.dump(self.scan_param, f)
        print("scan parameters: ", self.scan_param)
        print("saved to ", filename)


    def work(self, input_items, output_items):
        rx_vec = input_items[0]
        ref_vec = input_items[1]
        for i in range(len(rx_vec)):
            file_name_rx = "{}_rx_{}.dat".format(self.file_prefix, self.scan_index)
            file_name_ref = "{}_ref_{}.dat".format(self.file_prefix, self.scan_index)
            with open(file_name_rx,'wb') as f:
                f.write(rx_vec[i].tobytes())
            with open(file_name_ref, 'wb') as f:
                f.write(ref_vec[i].tobytes())
            self.scan_index += 1
        return len(input_items[0])
