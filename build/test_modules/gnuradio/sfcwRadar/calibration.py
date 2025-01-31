#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class calibration(gr.sync_block):
    """
    Block with parameters for file reading and vector processing.
    """

    def __init__(self, num_steps=128, cal_fileName = "cal_0.npy", isOff = False):
        gr.sync_block.__init__(
            self,
            name='Calibration',
            in_sig=[(np.complex64,num_steps)],
            out_sig=[(np.complex64,num_steps)],
        )

        self.num_steps = num_steps
        self.cal_fileName = cal_fileName
        self.isOff = isOff

        try:
            # Read reference and received samples
            self.cal_vector = np.load(self.cal_fileName)
            #print(self.ref_vector.shape)
            #print(self.cal_vector.shape)
            #print(self.cal_vector)

        except FileNotFoundError:
            print(f"Error: cal file not found.")
            # Handle the error appropriately, e.g., raise an exception or set a default value
            self.cal_vector = np.zeros(self.num_steps, dtype=np.complex64) # Example default
        if self.cal_vector.shape[0]!=self.num_steps:
            print(f"calibration vector size not equals to num_steps: ",self.cal_vector.shape)
            self.cal_vector = np.zeros(self.num_steps, dtype=np.complex64) # Example default

    def set_isOff(self,isOff):
        print("turning calibration off");
        self.isOff = isOff

    def work(self, input_items, output_items):
        in_vec = input_items[0]
        out_vec = output_items[0]
        #print(in_vec.shape)
        #print(in_vec)
        # Check input vector length
        if in_vec.shape[1] != self.num_steps:
            print(f"Warning: Input vector length ({len(in_vec)}) does not match num_steps ({self.num_steps}).")
            return 0  # Or handle the mismatch in another way
        if self.isOff:
            print("calibration is turned off")
            out_vec[:] = in_vec[:]
        else:
            for i in range(len(in_vec)):
                #out_vec[i][:] = in_vec[i][:] * np.conj(self.cal_vector)
                out_vec[:] = in_vec[i][:]/self.cal_vector
        return len(output_items)

