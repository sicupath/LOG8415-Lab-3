#!/bin/bash

# Update the package list
sudo apt-get update

# Install Python3 and pip if they are not already installed
sudo apt-get install -y python3 python3-pip

# Install AWS SDK for Python (Boto3) 
pip3 install boto3

# Run the gatekeeper.py script
python3 gatekeeper.py
