#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr
from scipy.signal import chirp, correlate

class channelResponseExtractor(gr.sync_block):
    """
    SFCW Channel Response Extractor

    This block processes SFCW radar signals to extract the calibrated channel
    response for each frequency step. It supports two sub-pulse modes.

    - Chirp Mode: Correlates both the echo and reference signals with an
      ideal local chirp to find their respective compressed peaks. It then
      divides the echo's peak by the reference's peak to get the calibrated
      channel response.
    - Pure Tone Mode: Performs phase compensation via complex division
      and averages the result to get a single channel estimate.

    Parameters
    ----------
    burst_len : int
        The number of IQ samples per sub-pulse (vector length).
    chirp_bandwidth : float
        The bandwidth of the LFM chirp sub-pulse (in Hz).
    samp_rate : float
        The sampling rate of the SDR's ADC (in Hz).
    isChirp : bool
        If True, use the chirp processing method.
        If False, use the pure tone processing method.
    """
    def __init__(self, burst_len: int, chirp_bandwidth: float, samp_rate: float, isChirp: bool):
        # Define I/O signatures. Two vector inputs, one scalar output.
        in_sig = [(np.complex64, burst_len), (np.complex64, burst_len)]
        out_sig = [np.complex64]

        gr.sync_block.__init__(
            self,
            name='Channel Response Extractor', #<-- Name updated here
            in_sig=in_sig,
            out_sig=out_sig,
        )

        # Store the mode selection flag
        self.isChirp = isChirp

        # --- Generate the ideal local chirp for the matched filter ---
        # This is created only once during initialization for efficiency.
        # It's only used if isChirp is True.
        pulse_duration = burst_len / samp_rate
        t = np.linspace(0, pulse_duration, burst_len, endpoint=False)
        self.local_chirp = chirp(
            t,
            f0=-chirp_bandwidth / 2,
            f1=chirp_bandwidth / 2,
            t1=pulse_duration,
            method='linear'
        ).astype(np.complex64)

    def _extract_channel_chirp(self, echo_vector, ref_vector):
        """
        Reimplements the method from the generate_ascan_from_lfm function.
        It finds the calibrated channel response for a single frequency step.
        """
        # --- Step 1: Find the uncalibrated peak from the echo signal ---
        # Correlate the incoming echo vector with the ideal local chirp
        cor_echo = correlate(echo_vector, self.local_chirp, mode='same')
        # Find the complex value at the correlation peak
        echo_peak = cor_echo[np.argmax(np.abs(cor_echo))]

        # --- Step 2: Find the reference peak for calibration ---
        # Correlate the incoming reference vector with the ideal local chirp
        cor_ref = correlate(ref_vector, self.local_chirp, mode='same')
        # Find the complex value at the correlation peak
        ref_peak = cor_ref[np.argmax(np.abs(cor_ref))]

        # --- Step 3: Perform Phase Coherence Compensation ---
        # Divide the echo's response by the reference's response
        epsilon = 1e-12
        calibrated_response = echo_peak / (ref_peak + epsilon)
        
        return calibrated_response

    def _extract_channel_tone(self, echo_vector, ref_vector):
        """
        Extracts channel response for pure tone sub-pulses via coherent averaging.
        """
        # Compensate echo by dividing by the reference
        compensated_vector = echo_vector *np.conjugate(ref_vector)
        
        # Average the compensated vector to get a single, robust estimate
        return np.mean(compensated_vector)

    def work(self, input_items, output_items):
        """
        Dispatcher: calls the appropriate processing function based on isChirp flag.
        """
        echo_vectors = input_items[0]
        ref_vectors = input_items[1]
        channel_out = output_items[0]

        # Determine which function to call
        if self.isChirp:
            processing_function = self._extract_channel_chirp
        else:
            processing_function = self._extract_channel_tone
            
        # Process each vector pair from the input buffers
        num_vectors = len(echo_vectors)
        for i in range(num_vectors):
            # Call the selected function with the current echo and reference vectors
            channel_out[i] = processing_function(echo_vectors[i], ref_vectors[i])

        return num_vectors
