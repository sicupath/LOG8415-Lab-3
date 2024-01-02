#!/bin/bash

# Update the package list
sudo apt-get update

# Install Python3 and pip if they are not already installed
sudo apt-get install -y python3 python3-pip

# Install the ping3 library for the proxy script
pip3 install ping3

# Run the proxy.py script
python3 /path/to/proxy.py