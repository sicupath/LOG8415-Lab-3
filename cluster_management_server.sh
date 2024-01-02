#!/bin/bash

# Update the list of packages available for installation
sudo apt update

# Install necessary libraries and sysbench, a benchmarking tool
sudo apt install libaio1 libmecab2 libncurses5 sysbench -y

# Change to the home directory of the 'ubuntu' user
cd /home/ubuntu

# Download the MySQL Cluster Management Server package
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Install the downloaded package
sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Create a directory to store MySQL Cluster data
sudo mkdir /var/lib/mysql-cluster

# Create a configuration file for the MySQL Cluster
echo "
[ndbd default]
NoOfReplicas=3 

[ndb_mgmd]
hostname=ip-172-31-22-6.ec2.internal 
datadir=/var/lib/mysql-cluster      
NodeId=1                            

[ndbd]
hostname=ip-172-31-22-7.ec2.internal 
NodeId=2                            
datadir=/usr/local/mysql/data       

[ndbd]
hostname=ip-172-31-22-8.ec2.internal 
NodeId=3                            
datadir=/usr/local/mysql/data       

[ndbd]
hostname=ip-172-31-22-9.ec2.internal 
NodeId=4                                     
datadir=/usr/local/mysql/data       

[mysqld]
hostname=ip-172-31-22-6.ec2.internal
nodeid=50
" | tee -a /var/lib/mysql-cluster/config.ini

# Create a systemd service for the MySQL Cluster Management Server
echo "
[Unit]
Description=MySQL NDB Cluster Management Server
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/sbin/ndb_mgmd -f /var/lib/mysql-cluster/config.ini
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
" | tee -a /etc/systemd/system/ndb_mgmd.service

# Reload systemd daemon, enable and start the MySQL Cluster Management Server
sudo systemctl daemon-reload
sudo systemctl enable ndb_mgmd
sudo systemctl start ndb_mgmd

# Download and extract the MySQL Cluster bundle
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar -C install/
cd install

# Install MySQL components from the bundle
sudo dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb

# Set up the MySQL server with a predefined root password
sudo debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/root-pass password ClusterPassword'
sudo debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/re-root-pass password ClusterPassword'
sudo debconf-set-selections <<< "mysql-cluster-community-server_7.6.6 mysql-server/default-auth-override select Use Legacy Authentication Method (Retain MySQL 5.x Compatibility)"

# Install MySQL server components
sudo dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb

# Configure MySQL to use the MySQL Cluster
echo "
[mysqld]
ndbcluster                      

[mysql_cluster]
ndb-connectstring=ip-172-31-17-1.ec2.internal  # location of management server
" | tee -a /etc/mysql/my.cnf

# Restart and enable the MySQL service
sudo systemctl restart mysql
sudo systemctl enable mysql

# Change back to the home directory, download and extract the Sakila sample database
cd ~
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xf sakila-db.tar.gz
rm sakila-db.tar.gz

# Load the Sakila database schema and data into MySQL
sudo mysql -u root -pClusterPassword -e "SOURCE sakila-db
/sakila-schema.sql;"
sudo mysql -u root -pClusterPassword -e "SOURCE sakila-db/sakila-data.sql;"