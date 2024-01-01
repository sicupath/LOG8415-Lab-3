#!/bin/bash

# Update the list of available packages and their versions
sudo apt-get update

# Install MySQL server and sysbench (a benchmarking tool)
sudo apt install mysql-server sysbench -y

# Download the Sakila sample database
wget https://downloads.mysql.com/docs/sakila-db.tar.gz 

# Unpack the downloaded tar.gz file containing the Sakila database
tar -xvf sakila-db.tar.gz 

# Remove the downloaded tar.gz file as it's no longer needed
rm sakila-db.tar.gz

# Load the Sakila database schema into MySQL
sudo mysql -e "SOURCE sakila-db/sakila-schema.sql;"

# Load the Sakila database data into MySQL
sudo mysql -e "SOURCE sakila-db/sakila-data.sql;"

# Select the Sakila database for use (not necessary for just loading data)
sudo mysql -e "USE sakila;"


