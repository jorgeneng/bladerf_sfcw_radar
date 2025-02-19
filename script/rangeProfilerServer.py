#!/usr/bin/env python
# coding=utf-8

import socket
import numpy as np
import matplotlib.pyplot as plt

def file_saving_server(host, port, filename_prefix):
    fig, axes = plt.subplots(1,2)
    b_scan_data = []
    max_b_scan_size = 32
    plt.ion()
    plt.show()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    file_counter = 0

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        while True:
            received_data = client_socket.recv(128*8)
            if not received_data:
                break
            rangeProfile = np.frombuffer(received_data, dtype = np.complex64)
            print(rangeProfile.shape)
            axes[0].clear()
            axes[0].plot(np.abs(rangeProfile)**2)
    
            b_scan_data.append(np.abs(rangeProfile)**2)
            if len(b_scan_data) > max_b_scan_size:
                b_scan_data.pop(0)

            b_scan_plot = np.array(b_scan_data)
            axes[1].clear()
            axes[1].imshow(b_scan_plot, aspect='auto',origin = 'lower')
            fig.canvas.flush_events()
        client_socket.close()

file_saving_server("localhost",9999,"received_data")
        
