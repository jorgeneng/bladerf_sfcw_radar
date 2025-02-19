#!/usr/bin/env python
# coding=utf-8
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import argparse

class FolderMonitor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.existing_files = set(os.listdir(folder_path))
        self.fig, self.axes = plt.subplots(1,2)  # Create figure and axes
        self.b_scan_data = []  # Store B-scan data
        self.max_b_scan_size = 32  # Maximum number of A-scans to keep 

    def monitor(self):
        plt.ion()
        plt.show()
        while True:
            current_files = set(os.listdir(self.folder_path))
            new_files = current_files - self.existing_files
            if new_files:
                for file_name in new_files:
                    file_path = os.path.join(self.folder_path, file_name)
                    try:
                        data = np.load(file_path)  # Read file into numpy array
                        print(f"New file detected: {file_name}")
                        print(data.shape)
                        self.axes[0].clear()
                        self.axes[0].plot(np.abs(data)**2)

                        # Append current A-scan to B-scan data
                        self.b_scan_data.append(np.abs(data))  # Use absolute value for B-scan 

                        # Keep only the most recent A-scans
                        if len(self.b_scan_data) > self.max_b_scan_size:
                            self.b_scan_data.pop(0)
                        
                        b_scan_plot = np.array(self.b_scan_data)
                        self.axes[1].clear()
                        self.axes[1].imshow(np.array(self.b_scan_data).T, aspect='auto', origin='lower')
                        self.fig.canvas.flush_events()
                    except Exception as e:
                        print(f"Error reading file {file_name}: {e}")

                self.existing_files = current_files  # Update existing files

            time.sleep(0.5)  # Check every second

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a folder for new files and plot the data.")
    parser.add_argument("folder_path", help="Path to the folder to monitor.")
    args = parser.parse_args() 
    monitor = FolderMonitor(args.folder_path)
    monitor.monitor()
