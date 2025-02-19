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
    def __init__(self, num_steps, prefix, upload_to_server, server_ip="localhost", server_port="9999"):
        gr.sync_block.__init__(self,
            name="rangeProfileSink",
            in_sig=[(np.complex64, num_steps)],
            out_sig=None)
        self.num_steps = num_steps
        self.prefix = prefix
        self.numScanReceived = 0
        self.upload_to_server = upload_to_server
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None
    
    def start(self):
        if self.upload_to_server:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_ip, self.server_port))
                return True # Indicate successful start
            except Exception as e:
                print(f"Network error during start: {e}")
                return False # Indicate error during start 

    def work(self, input_items, output_items):
        in_vec = input_items[0]
        #print(in_vec.shape)
        for i in range(len(in_vec)):
            if self.upload_to_server:
                if self.client_socket is None:
                    print("No connection to the server")
                    return 0
                self.client_socket.sendall(in_vec[i])
            filename = self.prefix + "_" + str(self.numScanReceived)
            np.save(filename, in_vec[i])
            self.numScanReceived += 1
        return len(input_items[0])
    
    def stop(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        return True
