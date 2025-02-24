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

    def __init__(self, burst_len=(2**10), freq_step=20e6, num_steps=128, range_profile_prefix='/home/hui/rangeProfile/scan', raw_signal_file_prefix='/home/hui/rawSignals/raw', recv_buf_len=(2**10+256), ref_gain=5, rx_gain=40, server_ip='localhost', server_port=9999, start_freq=2e9, tx_gain=20, upload_to_server=1):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.burst_len = burst_len
        self.freq_step = freq_step
        self.num_steps = num_steps
        self.range_profile_prefix = range_profile_prefix
        self.raw_signal_file_prefix = raw_signal_file_prefix
        self.recv_buf_len = recv_buf_len
        self.ref_gain = ref_gain
        self.rx_gain = rx_gain
        self.server_ip = server_ip
        self.server_port = server_port
        self.start_freq = start_freq
        self.tx_gain = tx_gain
        self.upload_to_server = upload_to_server

        ##################################################
        # Variables
        ##################################################
        self.chirp_bandwidth = chirp_bandwidth = 1e6
        self.transition_width = transition_width = chirp_bandwidth/2
        self.samp_rate = samp_rate = 5e6
        self.mf_size = mf_size = recv_buf_len
        self.lp_dec = lp_dec = 1
        self.cw_freq = cw_freq = 100e3
        self.cw_amp = cw_amp = 1
        self.cut_off = cut_off = chirp_bandwidth

        ##################################################
        # Blocks
        ##################################################

        self.sfcwRadar_rawSamplesSink_0 = sfcwRadar.rawSamplesSink(raw_signal_file_prefix, int(start_freq), num_steps, int(samp_rate), rx_gain, tx_gain, ref_gain, False, burst_len, recv_buf_len, cw_amp, cw_freq, True, chirp_bandwidth)
        self.sfcwRadar_rangeProfileSink_1 = sfcwRadar.rangeProfileSink(num_steps,range_profile_prefix,upload_to_server,server_ip,server_port)
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
        self.blocks_stream_to_vector_1_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (recv_buf_len*num_steps))
        self.blocks_stream_to_vector_1_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (recv_buf_len*num_steps))
        self.blocks_stream_to_vector_1_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(mf_size/lp_dec)))
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(mf_size/lp_dec)))
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.cons(pmt.PMT_NIL, pmt.from_long(2)), 1000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.sfcwRadar_bladerfRadarController_cc_0, 'scan'))
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

    def get_freq_step(self):
        return self.freq_step

    def set_freq_step(self, freq_step):
        self.freq_step = freq_step

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps

    def get_range_profile_prefix(self):
        return self.range_profile_prefix

    def set_range_profile_prefix(self, range_profile_prefix):
        self.range_profile_prefix = range_profile_prefix

    def get_raw_signal_file_prefix(self):
        return self.raw_signal_file_prefix

    def set_raw_signal_file_prefix(self, raw_signal_file_prefix):
        self.raw_signal_file_prefix = raw_signal_file_prefix
        self.sfcwRadar_rawSamplesSink_0.set_file_prefix(self.raw_signal_file_prefix)

    def get_recv_buf_len(self):
        return self.recv_buf_len

    def set_recv_buf_len(self, recv_buf_len):
        self.recv_buf_len = recv_buf_len
        self.set_mf_size(self.recv_buf_len)

    def get_ref_gain(self):
        return self.ref_gain

    def set_ref_gain(self, ref_gain):
        self.ref_gain = ref_gain
        self.sfcwRadar_bladerfRadarController_cc_0.set_ref_gain(self.ref_gain)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.sfcwRadar_bladerfRadarController_cc_0.set_rx_gain(self.rx_gain)

    def get_server_ip(self):
        return self.server_ip

    def set_server_ip(self, server_ip):
        self.server_ip = server_ip

    def get_server_port(self):
        return self.server_port

    def set_server_port(self, server_port):
        self.server_port = server_port

    def get_start_freq(self):
        return self.start_freq

    def set_start_freq(self, start_freq):
        self.start_freq = start_freq

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.sfcwRadar_bladerfRadarController_cc_0.set_tx_gain(self.tx_gain)

    def get_upload_to_server(self):
        return self.upload_to_server

    def set_upload_to_server(self, upload_to_server):
        self.upload_to_server = upload_to_server

    def get_chirp_bandwidth(self):
        return self.chirp_bandwidth

    def set_chirp_bandwidth(self, chirp_bandwidth):
        self.chirp_bandwidth = chirp_bandwidth
        self.set_cut_off(self.chirp_bandwidth)
        self.set_transition_width(self.chirp_bandwidth/2)
        self.sfcwRadar_bladerfRadarController_cc_0.set_chirp_bandwidth(self.chirp_bandwidth)

    def get_transition_width(self):
        return self.transition_width

    def set_transition_width(self, transition_width):
        self.transition_width = transition_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))

    def get_mf_size(self):
        return self.mf_size

    def set_mf_size(self, mf_size):
        self.mf_size = mf_size

    def get_lp_dec(self):
        return self.lp_dec

    def set_lp_dec(self, lp_dec):
        self.lp_dec = lp_dec

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



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--burst-len", dest="burst_len", type=intx, default=(2**10),
        help="Set burst_len [default=%(default)r]")
    parser.add_argument(
        "--freq-step", dest="freq_step", type=eng_float, default=eng_notation.num_to_str(float(20e6)),
        help="Set freq_step [default=%(default)r]")
    parser.add_argument(
        "--num-steps", dest="num_steps", type=intx, default=128,
        help="Set num_steps [default=%(default)r]")
    parser.add_argument(
        "--range-profile-prefix", dest="range_profile_prefix", type=str, default='/home/hui/rangeProfile/scan',
        help="Set range_profile_prefix [default=%(default)r]")
    parser.add_argument(
        "--raw-signal-file-prefix", dest="raw_signal_file_prefix", type=str, default='/home/hui/rawSignals/raw',
        help="Set raw_signal_file_prefix [default=%(default)r]")
    parser.add_argument(
        "--recv-buf-len", dest="recv_buf_len", type=intx, default=(2**10+256),
        help="Set recv_buf_len [default=%(default)r]")
    parser.add_argument(
        "--ref-gain", dest="ref_gain", type=intx, default=5,
        help="Set ref_gain [default=%(default)r]")
    parser.add_argument(
        "--rx-gain", dest="rx_gain", type=intx, default=40,
        help="Set rx_gain [default=%(default)r]")
    parser.add_argument(
        "--server-ip", dest="server_ip", type=str, default='localhost',
        help="Set server_ip [default=%(default)r]")
    parser.add_argument(
        "--server-port", dest="server_port", type=intx, default=9999,
        help="Set server_port [default=%(default)r]")
    parser.add_argument(
        "--start-freq", dest="start_freq", type=eng_float, default=eng_notation.num_to_str(float(2e9)),
        help="Set start_freq [default=%(default)r]")
    parser.add_argument(
        "--tx-gain", dest="tx_gain", type=intx, default=20,
        help="Set tx_gain [default=%(default)r]")
    parser.add_argument(
        "--upload-to-server", dest="upload_to_server", type=intx, default=1,
        help="Set upload_to_server [default=%(default)r]")
    return parser


def main(top_block_cls=sfcwRadarNoGUI, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(burst_len=options.burst_len, freq_step=options.freq_step, num_steps=options.num_steps, range_profile_prefix=options.range_profile_prefix, raw_signal_file_prefix=options.raw_signal_file_prefix, recv_buf_len=options.recv_buf_len, ref_gain=options.ref_gain, rx_gain=options.rx_gain, server_ip=options.server_ip, server_port=options.server_port, start_freq=options.start_freq, tx_gain=options.tx_gain, upload_to_server=options.upload_to_server)

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
