#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: v3.10.9.2-39-gcf065ee5

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sfcwRadar




class testRangeProfileSink(gr.top_block):

    def __init__(self, num_steps=128, server_ip='localhost', server_port=9999, upload_to_server=0):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.num_steps = num_steps
        self.server_ip = server_ip
        self.server_port = server_port
        self.upload_to_server = upload_to_server

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 5e6

        ##################################################
        # Blocks
        ##################################################

        self.sfcwRadar_rangeProfileSink_0 = sfcwRadar.rangeProfileSink(num_steps,'prefix',upload_to_server,server_ip,server_port)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, 128)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 100e3, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.sfcwRadar_rangeProfileSink_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_stream_to_vector_0, 0))


    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps

    def get_server_ip(self):
        return self.server_ip

    def set_server_ip(self, server_ip):
        self.server_ip = server_ip

    def get_server_port(self):
        return self.server_port

    def set_server_port(self, server_port):
        self.server_port = server_port

    def get_upload_to_server(self):
        return self.upload_to_server

    def set_upload_to_server(self, upload_to_server):
        self.upload_to_server = upload_to_server

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--num-steps", dest="num_steps", type=intx, default=128,
        help="Set num_steps [default=%(default)r]")
    parser.add_argument(
        "--server-ip", dest="server_ip", type=str, default='localhost',
        help="Set server_ip [default=%(default)r]")
    parser.add_argument(
        "--server-port", dest="server_port", type=intx, default=9999,
        help="Set server_port [default=%(default)r]")
    parser.add_argument(
        "--upload-to-server", dest="upload_to_server", type=intx, default=0,
        help="Set upload_to_server [default=%(default)r]")
    return parser


def main(top_block_cls=testRangeProfileSink, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(num_steps=options.num_steps, server_ip=options.server_ip, server_port=options.server_port, upload_to_server=options.upload_to_server)

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
