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

    def __init__(self, num_steps=128, burst_len=2048, ref_fileName="cal_ref_1.dat", rx_fileName="cal_ref_0.dat", isOff = False):
        gr.sync_block.__init__(
            self,
            name='Calibration',
            in_sig=[(np.complex64,num_steps)],
            out_sig=[(np.complex64,num_steps)],
        )

        self.num_steps = num_steps
        self.burst_len = burst_len
        self.ref_fileName = ref_fileName
        self.rx_fileName = rx_fileName
        self.isOff = isOff
        supposed_size = burst_len*num_steps 

        try:
            # Read reference and received samples
            self.ref_samples = np.fromfile(self.ref_fileName, dtype=np.complex64)
            N = supposed_size - self.ref_samples.size
            #.reshape(self.num_steps, self.burst_len)
            if N>=0:
                self.ref_samples = np.pad(self.ref_samples,(0,N),'constant')
            else:
                self.ref_samples = self.ref_samples[0:supposed_size]

            self.ref_samples = self.ref_samples.reshape(self.num_steps,self.burst_len)

            self.rx_samples = np.fromfile(self.rx_fileName, dtype=np.complex64)#.reshape(self.num_steps, self.burst_len)
            N = supposed_size - self.rx_samples.size
            #.reshape(self.num_steps, self.burst_len)
            if N>=0:
                self.rx_samples = np.pad(self.rx_samples,(0,N),'constant')
            else:
                self.rx_samples = self.rx_samples[0:supposed_size]

            self.rx_samples = self.rx_samples.reshape(self.num_steps,self.burst_len)

            # Multiply rx_samples with conjugate of ref_samples
            prod = self.rx_samples * np.conj(self.ref_samples)

            # Calculate mean of each row
            self.ref_vector = np.mean(prod, axis=1)

            #print(self.ref_vector.shape)
            print(self.ref_vector.shape)

        except FileNotFoundError:
            print(f"Error: One or both files ({self.ref_fileName}, {self.rx_fileName}) not found.")
            # Handle the error appropriately, e.g., raise an exception or set a default value
            self.ref_vector = np.zeros(self.num_steps, dtype=np.complex64) # Example default

    def set_isOff(self,isOff):
        print("turning calibration off");
        self.isOff = isOff

    def work(self, input_items, output_items):
        in_vec = input_items[0]
        out_vec = output_items[0]
        # print(in_vec.shape)
        # Check input vector length
        if in_vec.shape[1] != self.num_steps:
            print(f"Warning: Input vector length ({len(in_vec)}) does not match num_steps ({self.num_steps}).")
            return 0  # Or handle the mismatch in another way
        if self.isOff:
            print("calibration is turned off")
            out_vec[:] = in_vec[:]
        else:
            out_vec[:] = in_vec[0,:] * np.conj(self.ref_vector)
            #out_vec[:] = in_vec[0,:]/self.ref_vector
        return len(output_items)
