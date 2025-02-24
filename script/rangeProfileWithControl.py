#!/usr/bin/env python
# coding=utf-8
import matplotlib.pyplot as plt
import numpy as np
import socket
import time
#import keyboard #install keyboard library with pip install keyboard

# --- Configuration ---
HOST = 'remote_machine_ip'
PORT = 65432
ASCAN_LENGTH = 100

# --- Setup Socket ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# --- Setup Plotting ---
plt.ion()
fig, ax = plt.subplots()
bscan_data = []
vmin = 0  # Initial vmin
vmax = 100 # Initial vmax
image = None #initialize the image variable

# --- Main Loop ---
while True:
    try:
        # Receive A-scan data
        data = s.recv(ASCAN_LENGTH * 4)
        if not data:
            break
        ascan = np.frombuffer(data, dtype=np.float32)

        # Update B-scan data
        bscan_data.append(ascan)
        if len(bscan_data) > 200:
            bscan_data.pop(0)

        # Plot B-scan
        if image is None:
            image = ax.imshow(np.array(bscan_data), aspect='auto', origin='lower', vmin=vmin, vmax=vmax)
        else:
            image.set_data(np.array(bscan_data))
            image.set_clim(vmin=vmin, vmax=vmax)

        plt.pause(0.01)

        # Keyboard input for vmin and vmax control
        """
        if keyboard.is_pressed('q'): #lower vmin
            vmin -=1
            print(f"vmin: {vmin}, vmax: {vmax}")
            time.sleep(0.1)
        if keyboard.is_pressed('w'): #raise vmin
            vmin +=1
            print(f"vmin: {vmin}, vmax: {vmax}")
            time.sleep(0.1)
        if keyboard.is_pressed('a'): #lower vmax
            vmax -= 1
            print(f"vmin: {vmin}, vmax: {vmax}")
            time.sleep(0.1)
        if keyboard.is_pressed('s'): #raise vmax
            vmax += 1
            print(f"vmin: {vmin}, vmax: {vmax}")
            time.sleep(0.1)
        """
    except ConnectionResetError:
        print("Connection closed by remote host.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        break

s.close()
