#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
from scipy import signal
from pylab import *

class matchedFilter(gr.sync_block):
    """
    docstring for block matchedFilter
    """
    def __init__(self, mf_size):
        gr.sync_block.__init__(self,
            name="matchedFilter",
            in_sig=[(np.complex64,mf_size),(np.complex64,mf_size)],
            out_sig=[(np.complex64,mf_size)],
        )

        self.burst_len = mf_size

    def fix_iq_imbalance(self, x):
        # remove DC and save input power
        z = x - mean(x)
        p_in = var(z)

        # scale Q to have unit amplitude (remember we're assuming a single input tone)
        Q_amp = sqrt(2*mean(x.imag**2))
        z /= Q_amp

        I, Q = z.real, z.imag

        alpha_est = sqrt(2*mean(I**2))
        sin_phi_est = (2/alpha_est)*mean(I*Q)
        cos_phi_est = sqrt(1 - sin_phi_est**2)

        I_new_p = (1/alpha_est)*I
        Q_new_p = (-sin_phi_est/alpha_est)*I + Q

        y = (I_new_p + 1j*Q_new_p)/cos_phi_est

        #print ('phase error:', arccos(cos_phi_est)*360/2/pi, 'degrees')
        #print ('amplitude error:', 20*log10(alpha_est), 'dB')

        return y*sqrt(p_in/var(y))

    def normaliseBurst(self,input_burst):
        burst_real = np.real(input_burst)
        burst_imag = np.imag(input_burst)
        max_val = np.max(burst_real)
        min_val = np.min(burst_real)
        burst_real_normalised = 2*(burst_real - min_val)/(max_val - min_val)-1
        max_val = np.max(burst_imag)
        min_val = np.min(burst_imag)
        burst_imag_normalised = 2*(burst_imag - min_val)/(max_val - min_val)-1
        return burst_real_normalised + 1j*burst_imag_normalised 

    def work(self, input_items, output_items):
        rx_vec = input_items[0]
        ref_vec = input_items[1]
        out_vec = output_items[0]
        #print(rx_vec.shape)
        #print(out_vec.shape)
        if rx_vec.shape[1] != self.burst_len:
            print(f"Warning: Input vector length ({len(in_vec)}) does not match mf_size ({self.burst_len}).")
            return 0  # Or handle the mismatch in another way
        for i in range(len(rx_vec)):
            rx_sample = rx_vec[i][:]/np.linalg.norm(rx_vec[i][:])
            ref_sample = ref_vec[i][:]/np.linalg.norm(ref_vec[i][:])
            out_vec[i][:] = signal.correlate(rx_sample,ref_sample,mode='same')

            #norm_factor = sqrt(sum(np.abs(rx_vec[i][:])*sum(np.abs(ref_vec[i][:])))) 
            #out_vec[i][:] = signal.correlate(rx_vec[i][:],ref_vec[i][:],mode='same')/norm_factor
        return len(output_items[0])
