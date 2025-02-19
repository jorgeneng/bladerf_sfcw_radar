#!/usr/bin/env python
# coding=utf-8
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import argparse
import paramiko
from scp import SCPClient

class FolderMonitor:
    def __init__(self, folder_path, host, usr, password, remote_path):
        self.folder_path = folder_path
        self.existing_files = set(os.listdir(folder_path))
        #self.existing_files = {os.path.abspath(os.path.join(self.folder_path, f)) for f in os.listdir(self.folder_path)} 
        print(self.existing_files)
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname = host, username = usr, password = password)
        self.scp_client = SCPClient(self.ssh_client.get_transport())
        self.remote_path = remote_path
        print("init finished")

    def monitor(self):
        while True:
            current_files = set(os.listdir(self.folder_path))
            #current_files = {os.path.abspath(os.path.join(self.folder_path, f)) for f in os.listdir(self.folder_path)} 
            new_files = current_files - self.existing_files
            if new_files:
                #try:
                #    self.scp_client.put(new_files,remote_path=self.remote_path)
                #    print('sent '+str(len(new_files)) + ' files')
                #except Exception as e:
                #    print(f"Error reading file {file_name}: {e}")
                for file_name in new_files:
                    file_path = os.path.join(self.folder_path, file_name)
                    try:
                        print(f"New file detected: {file_name}")
                        #scp_client = SCPClient(self.ssh_client.get_transport())
                        self.scp_client.put(file_path,remote_path = self.remote_path)
                        #scp_client.close()
                    except Exception as e:
                        print(f"Error reading file {file_name}: {e}")

                self.existing_files = current_files  # Update existing files

            time.sleep(0.5)  # Check every second

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a folder for new files and plot the data.")
    parser.add_argument("folder_path", help="Path to the folder to monitor.")
    args = parser.parse_args() 
    monitor = FolderMonitor(args.folder_path,'10.42.0.229','ubadmin','ubadmin','/home/ubadmin/testFolder/')
    monitor.monitor()
