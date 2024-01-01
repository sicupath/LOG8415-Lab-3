import time
import boto3
from ec2_instances import *
from security_groups import *
import paramiko
import subprocess

def main():
        
    # Initialize AWS EC2 client and resource
    print("Initializing client and resource")
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    ec2_resource = boto3.resource("ec2", region_name="us-east-1")
    
    # Get the default VPC ID (function declared later) and create a security group
    print("Creating standalone security group")
    vpc_id = get_default_vpc_id(ec2_client)
    security_group = create_standalone_security_group(ec2_client, "standalone_group", vpc_id)
    time.sleep(60) # Wait for the security group to be fully created
    # Get the security group ID
    security_group_id = security_group['GroupId']
    print("Security group created successfully")

    # Create an EC2 instance with the provided security group and a subnet 
    instance = create_standalone_instance(ec2_resource, security_group_id, '172.31.64.9')
    
    # Wait for the instance to be fully initialized and ready
    print("Waiting for standalone instance to be ready...")
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance_id])
    # Get the instance ID
    instance_id = instance[0].id
    
    # Retrieve the public IP address of the created instance
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations']
    public_ip = reservations[0]["Instances"][0].get('PublicIpAddress')
    
    # Perform benchmark tests and retrieve results
    perform_benchmark(public_ip)
    retrieve_benchmark_results(public_ip)

    # Cleanup: Terminate the EC2 instance and security group                     
    print("Terminating instance")
    ec2_client.terminate_instances(InstanceIds=(instance_id))
    time.sleep(180) # Time for instance to be completely gone
    print("Terminating security group")
    ec2_client.delete_security_group(GroupId=security_group_id)


# Complementary functions

def get_default_vpc_id(ec2_client):
    # Retrieve the ID of the default Virtual Private Cloud (VPC)
    return ec2_client.describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')

def perform_benchmark(public_ip):
    # Perform benchmark tests on the instance
    print("Performing Standalone benchmark")
    execute_benchmark_commands(public_ip, [
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root prepare",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --num-threads=6 --max-time=60 --max-requests=0 run > standalone_benchmark.txt", 
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root cleanup"
    ])

def execute_benchmark_commands(public_ip, commands):
    # Connect to the instance via SSH and execute the given commands
    key = paramiko.RSAKey.from_private_key_file("key.pem")
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSHClient.connect(public_ip, username='ubuntu', pkey=key)
    
    for command in commands:
        stdin, stdout, stderror = SSHClient.exec_command(command)

def retrieve_benchmark_results(public_ip):
    # Retrieve the benchmark results file from the instance to the local machine
    print("Getting benchmark results")
    subprocess.call(['scp', '-o','StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', 'key.pem', f"ubuntu@{public_ip}:standalone_benchmark.txt", '.'])
    
main()