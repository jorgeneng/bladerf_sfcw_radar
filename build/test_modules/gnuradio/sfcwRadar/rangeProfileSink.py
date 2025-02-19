#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import socket
import numpy as np
from gnuradio import gr

class rangeProfileSink(gr.sync_block):
    """
    docstring for block rangeProfileSink
    """
    def __init__(self, num_steps, prefix):
        gr.sync_block.__init__(self,
            name="rangeProfileSink",
            in_sig=[(np.complex64, num_steps)],
            out_sig=None)
        self.num_steps = num_steps
        self.prefix = prefix
        self.numScanReceived = 0
        self.server_ip = 'localhost'
        self.server_port = 9999
        self.client_socket = None
    
    def start(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            return True # Indicate successful start
        except Exception as e:
            print(f"Network error during start: {e}")
            return False # Indicate error during start 

    def work(self, input_items, output_items):
        if self.client_socket is None:
            return 0
        in_vec = input_items[0]
        print(in_vec.shape)
        for i in range(len(in_vec)):
            #filename = self.prefix + "_" + str(self.numScanReceived)
            #np.save(filename, in_vec[i])
            self.client_socket.sendall(in_vec[i])
            self.numScanReceived += 1
        return len(input_items[0])
    def stop(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        return True
