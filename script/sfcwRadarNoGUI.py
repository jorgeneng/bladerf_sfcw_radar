#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: v3.10.9.2-39-gcf065ee5

from gnuradio import blocks
import pmt
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sfcwRadar




class sfcwRadarNoGUI(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.burst_len = burst_len = 2**11
        self.recv_buf_len = recv_buf_len = burst_len+512
        self.chirp_bandwidth = chirp_bandwidth = 1e6
        self.tx_gain = tx_gain = 20
        self.transition_width = transition_width = chirp_bandwidth/2
        self.start_freq = start_freq = 2e9
        self.samp_rate = samp_rate = 5e6
        self.rx_gain = rx_gain = 40
        self.ref_gain = ref_gain = 5
        self.num_steps = num_steps = 128
        self.mf_size = mf_size = recv_buf_len
        self.lp_dec = lp_dec = 1
        self.freq_step = freq_step = 20e6
        self.cw_freq = cw_freq = 100e3
        self.cw_amp = cw_amp = 1
        self.cut_off = cut_off = chirp_bandwidth

        ##################################################
        # Blocks
        ##################################################

        self.sfcwRadar_rawSamplesSink_0 = sfcwRadar.rawSamplesSink('raw', int(start_freq), num_steps, int(samp_rate), rx_gain, tx_gain, ref_gain, False, burst_len, recv_buf_len, cw_amp, cw_freq, True, chirp_bandwidth)
        self.sfcwRadar_rangeProfileSink_1 = sfcwRadar.rangeProfileSink(num_steps,'rangeProfile/scan',,'localhost',9999)
        self.sfcwRadar_matchedFilter_0 = sfcwRadar.matchedFilter((int(mf_size/lp_dec)))
        self.sfcwRadar_findPeak_0 = sfcwRadar.findPeak((int(mf_size/lp_dec)))
        self.sfcwRadar_bladerfRadarController_cc_0 = sfcwRadar.bladerfRadarController_cc(int(start_freq), num_steps, int(freq_step), int(samp_rate), rx_gain, tx_gain, ref_gain, True, burst_len, recv_buf_len, 8, 2048, 4, cw_amp, cw_freq, True, chirp_bandwidth, 1, 0)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            lp_dec,
            firdes.low_pass(
                1,
                samp_rate,
                cut_off,
                transition_width,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            lp_dec,
            firdes.low_pass(
                1,
                samp_rate,
                cut_off,
                transition_width,
                window.WIN_HAMMING,
                6.76))
        self.fft_vxx_0 = fft.fft_vcc(num_steps, False, window.hamming(num_steps), True, 1)
        self.blocks_var_to_msg_0 = blocks.var_to_msg_pair('scan_cont')
        self.blocks_stream_to_vector_1_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (recv_buf_len*num_steps))
        self.blocks_stream_to_vector_1_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (recv_buf_len*num_steps))
        self.blocks_stream_to_vector_1_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(mf_size/lp_dec)))
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(mf_size/lp_dec)))
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("TEST"), 1000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_var_to_msg_0, 'msgout'), (self.sfcwRadar_bladerfRadarController_cc_0, 'scan'))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.sfcwRadar_matchedFilter_0, 1))
        self.connect((self.blocks_stream_to_vector_1_0, 0), (self.sfcwRadar_matchedFilter_0, 0))
        self.connect((self.blocks_stream_to_vector_1_0_0, 0), (self.sfcwRadar_rawSamplesSink_0, 1))
        self.connect((self.blocks_stream_to_vector_1_0_1, 0), (self.sfcwRadar_rawSamplesSink_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.sfcwRadar_rangeProfileSink_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_stream_to_vector_1_0, 0))
        self.connect((self.sfcwRadar_bladerfRadarController_cc_0, 0), (self.blocks_stream_to_vector_1_0_0, 0))
        self.connect((self.sfcwRadar_bladerfRadarController_cc_0, 1), (self.blocks_stream_to_vector_1_0_1, 0))
        self.connect((self.sfcwRadar_bladerfRadarController_cc_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.sfcwRadar_bladerfRadarController_cc_0, 1), (self.low_pass_filter_0_0, 0))
        self.connect((self.sfcwRadar_findPeak_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.sfcwRadar_matchedFilter_0, 0), (self.sfcwRadar_findPeak_0, 0))


    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len
        self.set_recv_buf_len(self.burst_len+512)

    def get_recv_buf_len(self):
        return self.recv_buf_len

    def set_recv_buf_len(self, recv_buf_len):
        self.recv_buf_len = recv_buf_len
        self.set_mf_size(self.recv_buf_len)

    def get_chirp_bandwidth(self):
        return self.chirp_bandwidth

    def set_chirp_bandwidth(self, chirp_bandwidth):
        self.chirp_bandwidth = chirp_bandwidth
        self.set_cut_off(self.chirp_bandwidth)
        self.set_transition_width(self.chirp_bandwidth/2)
        self.sfcwRadar_bladerfRadarController_cc_0.set_chirp_bandwidth(self.chirp_bandwidth)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.sfcwRadar_bladerfRadarController_cc_0.set_tx_gain(self.tx_gain)

    def get_transition_width(self):
        return self.transition_width

    def set_transition_width(self, transition_width):
        self.transition_width = transition_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))

    def get_start_freq(self):
        return self.start_freq

    def set_start_freq(self, start_freq):
        self.start_freq = start_freq

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.sfcwRadar_bladerfRadarController_cc_0.set_rx_gain(self.rx_gain)

    def get_ref_gain(self):
        return self.ref_gain

    def set_ref_gain(self, ref_gain):
        self.ref_gain = ref_gain
        self.sfcwRadar_bladerfRadarController_cc_0.set_ref_gain(self.ref_gain)

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps

    def get_mf_size(self):
        return self.mf_size

    def set_mf_size(self, mf_size):
        self.mf_size = mf_size

    def get_lp_dec(self):
        return self.lp_dec

    def set_lp_dec(self, lp_dec):
        self.lp_dec = lp_dec

    def get_freq_step(self):
        return self.freq_step

    def set_freq_step(self, freq_step):
        self.freq_step = freq_step

    def get_cw_freq(self):
        return self.cw_freq

    def set_cw_freq(self, cw_freq):
        self.cw_freq = cw_freq

    def get_cw_amp(self):
        return self.cw_amp

    def set_cw_amp(self, cw_amp):
        self.cw_amp = cw_amp

    def get_cut_off(self):
        return self.cut_off

    def set_cut_off(self, cut_off):
        self.cut_off = cut_off
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))




def main(top_block_cls=sfcwRadarNoGUI, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
