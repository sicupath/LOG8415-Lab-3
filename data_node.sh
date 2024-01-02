#!/bin/bash

# Update the package list to ensure we have the latest versions of packages and their dependencies
sudo apt update

# Install necessary Perl library and ncurses library which are prerequisites for MySQL Cluster
sudo apt install libclass-methodmaker-perl libncurses5 -y

# Change the working directory to the home directory of the 'ubuntu' user
cd /home/ubuntu

# Download the MySQL Cluster Data Node package
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

# Install the downloaded MySQL Cluster Data Node package
sudo dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

# Configure the MySQL Cluster by appending the configuration to the my.cnf file
echo "
[mysql_cluster]
ndb-connectstring=ip-172-31-22-6.ec2.internal 
" | tee -a /etc/my.cnf

# Create a directory for MySQL data
sudo mkdir -p /usr/local/mysql/data

# Create a new systemd service file for the MySQL NDB Data Node Daemon
echo "
[Unit]
Description=MySQL NDB Data Node Daemon
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/sbin/ndbd
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
" | tee -a /etc/systemd/system/ndbd.service

# Reload the systemd daemon to recognize the new service
sudo systemctl daemon-reload

# Enable the newly created service to start on boot
sudo systemctl enable ndbd

# Start the MySQL NDB Data Node service immediately
sudo systemctl start ndbd
