#!/bin/bash


sudo apt update
sudo apt install libaio1 libmecab2 libncurses5 sysbench -y


wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb


sudo mkdir /var/lib/mysql-cluster

echo "
[ndbd default]
# Options affecting ndbd processes on all data nodes:
NoOfReplicas=3 # Number of replicas

[ndb_mgmd]
# Management process options:
hostname=ip-172-31-17-1.ec2.internal # Hostname of manager
datadir=/var/lib/mysql-cluster      # Directory for the log files
NodeId=1                            # Node ID for this data node

[ndbd]
hostname=ip-172-31-17-2.ec2.internal # Hostname/IP of the first data node
NodeId=2                            # Node ID for this data node
datadir=/usr/local/mysql/data       # Remote directory for the data files

[ndbd]
hostname=ip-172-31-17-3.ec2.internal # Hostname/IP of the second data node
NodeId=3                            # Node ID for this data node
datadir=/usr/local/mysql/data       # Remote directory for the data files

[ndbd]
hostname=ip-172-31-17-4.ec2.internal # Hostname/IP of the third data node
NodeId=4                            # Node ID for this data node           
datadir=/usr/local/mysql/data       # Remote directory for the data files


[mysqld]
# SQL node options:
hostname=ip-172-31-17-1.ec2.internal
nodeid=50
" | tee -a /var/lib/mysql-cluster/config.ini


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


sudo systemctl daemon-reload
sudo systemctl enable ndb_mgmd
sudo systemctl start ndb_mgmd


wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar -C install/
cd install

sudo dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb

# Based on: https://gist.github.com/ziadoz/dc935a0167c68fc23b4f35ee8593125f
# To automatate assigning a password
sudo debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/root-pass password ClusterPassword'
sudo debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/re-root-pass password ClusterPassword'
sudo debconf-set-selections <<< "mysql-cluster-community-server_7.6.6 mysql-server/default-auth-override select Use Legacy Authentication Method (Retain MySQL 5.x Compatibility)"

sudo dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb


echo "
[mysqld]
# Options for mysqld process:
ndbcluster                      # run NDB storage engine

[mysql_cluster]
# Options for NDB Cluster processes:
ndb-connectstring=ip-172-31-17-1.ec2.internal  # location of management server
" | tee -a /etc/mysql/my.cnf


sudo systemctl restart mysql
sudo systemctl enable mysql


cd ~
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xf sakila-db.tar.gz
rm sakila-db.tar.gz

sudo mysql -u root -pClusterPassword -e "SOURCE sakila-db/sakila-schema.sql;"
sudo mysql -u root -pClusterPassword -e "SOURCE sakila-db/sakila-data.sql;"