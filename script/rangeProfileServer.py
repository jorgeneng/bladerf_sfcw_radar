#!/usr/bin/env python
# coding=utf-8

import socket
import numpy as np
import matplotlib.pyplot as plt
import argparse
#import keyboard #install keyboard lib with pip install keyboard
from sklearn import decomposition

def range_profile_server(host, port, num_steps, vmin, vmax, max_b_scan_size):
    fig, axes = plt.subplots(1,3)
    b_scan_data = []
    plt.ion()
    plt.show()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        while True:
            received_data = b''
            while len(received_data) < num_steps*8:
                chunk = client_socket.recv(num_steps*8 - len(received_data))
                if not chunk:
                    break
                received_data += chunk
            if not received_data:
                break
            #print(received_data.shape)
            
            rangeProfile = np.frombuffer(received_data, dtype = np.complex64)
            axes[0].clear()
            axes[0].plot(np.abs(rangeProfile)**2)
    
            b_scan_data.append(np.abs(rangeProfile)**2)
            if len(b_scan_data) > max_b_scan_size:
                b_scan_data.pop(0)
                b_scan_pca = np.transpose(np.array(b_scan_plot))
                u, s, v = decomposition.randomized_svd(np.abs(b_scan_pca), 1) 
                low_rank = u @ np.diag(s) @ v 
                axes[2].clear()
                axes[2].imshow(b_scan_pca-low_rank, aspect='auto',cmap='jet', vmin=vmin, vmax=vmax) 

            b_scan_plot = np.array(b_scan_data)
            axes[1].clear()
            axes[1].imshow(b_scan_plot, aspect='auto',origin = 'lower', vmin=vmin, vmax=vmax)

            fig.canvas.flush_events()
            """
            if keyboard.is_pressed('q'):
                vmin -=1
                print(f"vmin: {vmin}, vmax: {vmax}")
            if keyboard.is_pressed('w'):
                vmin +=1
                print(f"vmin: {vmin}, vmax: {vmax}")
            if keyboard.is_pressed('a'):
                vmax -=1
                print(f"vmin: {vmin}, vmax: {vmax}")
            if keyboard.is_pressed('s'):
                vmax +=1
                print(f"vmin: {vmin}, vmax: {vmax}")
            """
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Range profile server.")
    parser.add_argument("host", help="Host IP address")
    parser.add_argument("port", type=int, help="Port number")
    parser.add_argument("num_steps", type=int, help="Filename prefix")
    parser.add_argument("vmin", type=int, help="min value of b_scan")
    parser.add_argument("vmax", type=int, help="max value of b_scan")
    parser.add_argument("--max_b_scan_size", type=int, default=32, help="maximum size of A-scans to plot the B-scan(default: 32)")

    args = parser.parse_args()

    range_profile_server(args.host, args.port, args.num_steps, args.vmin, args.vmax, args.max_b_scan_size)        
