import time
import boto3
from ec2_instances import *
from security_groups import *
import sys
import paramiko
import subprocess

def main():
    
    # Initialize AWS EC2 client and resource for interacting with AWS
    print("Initializing client and resource")
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    ec2_resource = boto3.resource("ec2", region_name="us-east-1")
    
    # Get the default VPC ID (function declared later) and create a security group
    print("Creating cluster security group")
    vpc_id = get_default_vpc_id(ec2_client)
    security_group = create_cluster_security_group(ec2_client,"cluster_group",vpc_id)
    time.sleep(60) # Wait for the security group to be fully created
    # Get the security group ID
    security_group_id = security_group['GroupId']
    print("Security group created successfully")

    # Create instances for the cluster: one master node and three slave or data nodes.
    master = create_cluster_instance(ec2_resource, "172.31.22.6", security_group_id, open('cluster_management_setup.sh').read(), "Master")
    slaves = [
        create_cluster_instance(ec2_resource, "172.31.22.7", security_group_id, open('data_node.sh').read(), "Slave-1"),
        create_cluster_instance(ec2_resource, "172.31.22.8", security_group_id, open('data_node.sh').read(), "Slave-2"),
        create_cluster_instance(ec2_resource, "172.31.22.9", security_group_id, open('data_node.sh').read(), "Slave-3")
    ]

    print("Waiting for cluster instances to be ready")
    # Wait until all instances are fully operational.
    instances_ids = [master[0].id] + [node[0].id for node in slaves]
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=instances_ids)
    
    # Get the public IP address of the master node.
    reservations = ec2_client.describe_instances(InstanceIds=[master[0].id])['Reservations']
    master_ip = reservations[0]["Instances"][0].get('PublicIpAddress')
    
    time.sleep(180)  # Wait for a while before starting the benchmark
    
    # Perform benchmark tests on the master node and retrieve the results.
    perform_benchmark(master_ip)

    # Terminate the cluster and clean up resources
    print("Terminating cluster")
    for id in instances_ids:
        ec2_client.terminate_instances(InstanceIds=(id))
    time.sleep(180) # Time for instances to be completely gone
    print("Terminating security group")
    ec2_client.delete_security_group(GroupId=security_group['GroupId'])


# Complementary functions

def get_default_vpc_id(ec2_client):
    # Retrieve the ID of the default Virtual Private Cloud (VPC)
    return ec2_client.describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')

def perform_benchmark(public_ip):
    # Perform benchmark tests on the cluster
    print("Performing Cluster benchmark")
    # Set up an SSH connection and execute benchmark commands on the given IP address.
    key = paramiko.RSAKey.from_private_key_file("key.pem")
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSHClient.connect(public_ip, username='ubuntu', pkey=key)

    commands = [
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster prepare",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster --num-threads=6 --max-time=60 --max-requests=0 run > cluster_benchmarking.txt", 
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster cleanup"
    ]
    for command in commands:
        SSHClient.exec_command(command)
    
    print("Getting benchmark results")
    subprocess.call(['scp', '-o','StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', 'key.pem', f"ubuntu@{ip}:cluster_benchmarking.txt", '.'])


main()