import sys
import time
import boto3
import paramiko
import subprocess
from ec2_instances import *
from security_groups import *


def main():
    
    if len(sys.argv) < 2:
        print('ERROR! Make sure the command has the (172.31.16.0/20) subnet, like this => python3 cluster.py "subnet-XXXXXXXXXXXXXXXXX"')
        exit()
        
    subnet_id = str(sys.argv[1])
    
    ec2_client = boto3.client("ec2", region_name="us-east-1")

    ec2_resource = boto3.resource("ec2", region_name="us-east-1")
    
    #get vpc_id
    vpc_id = ec2_client.describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')
     # create security group
    security_group = create_cluster_security_group(ec2_client,"cluster_group",vpc_id)
    
    time.sleep(10)

    # Create cluster
    master_node = create_cluster_instance(ec2_resource, "172.31.17.1", security_group['GroupId'], open('master_setup.sh').read(), "Master-Node", subnet_id)
    slave_node1 = create_cluster_instance(ec2_resource, "172.31.17.2", security_group['GroupId'], open('slave_setup.sh').read(), "Slave-Node1", subnet_id)
    slave_node2 = create_cluster_instance(ec2_resource, "172.31.17.3", security_group['GroupId'], open('slave_setup.sh').read(), "Slave-Node2", subnet_id)
    slave_node3 = create_cluster_instance(ec2_resource, "172.31.17.4", security_group['GroupId'], open('slave_setup.sh').read(), "Slave-Node3", subnet_id)

    print("Waiting for cluster instances to be ok...")
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[master_node[0].id])
    waiter.wait(InstanceIds=[slave_node1[0].id])
    waiter.wait(InstanceIds=[slave_node2[0].id])
    waiter.wait(InstanceIds=[slave_node3[0].id])
    
    # Get master node public IP
    reservations = ec2_client.describe_instances(InstanceIds=[master_node[0].id])['Reservations']
    ip = reservations[0]["Instances"][0].get('PublicIpAddress')
    
    time.sleep(180)
    
    print("CLUSTER BENCHMARK:")
    
    key = paramiko.RSAKey.from_private_key_file("labsuser.pem")
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    SSHClient.connect(ip, username='ubuntu', pkey=key)
    print('Connected to: ' + str(ip))

    commands = [
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster prepare",
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster --num-threads=6 --max-time=60 --max-requests=0 run > clusterBenchmark.txt", 
        "sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password=ClusterPassword --mysql_storage_engine=ndbcluster cleanup"
    ]
    for command in commands:
        # print("Executing "+ command)
        stdin , stdout, stderr = SSHClient.exec_command(command)
        print(stdout.read())
        print(stderr.read())
    
    print("SCP the benchmark results into local folder...")
    subprocess.call(['scp', '-o','StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', 'labsuser.pem', "ubuntu@" + str(ip) + ":clusterBenchmark.txt", '.'])
    
    
    destroy = False
    while destroy == False:
        answer = input("- Enter 'terminate' to terminate the instances and security group: ")
        if answer == "terminate":
            print("Terminating cluster instances...")
            terminate_instance(ec2_client, [master_node[0].id])
            terminate_instance(ec2_client, [slave_node1[0].id])
            terminate_instance(ec2_client, [slave_node2[0].id])
            terminate_instance(ec2_client, [slave_node3[0].id])
            print("Giving 3 min to make sure vpc endpoints from instances are gone before deleting security group...")
            time.sleep(180)
            print("Terminating security group...")
            delete_security_group(ec2_client, security_group['GroupId'])
            destroy = True
        else:
            continue
    
main()