import socket
import threading
import random
import boto3
import time
from ec2_instances import *
from security_groups import *

class GatekeeperServer:
    def __init__(self, host, port, nodes, trusted_hosts):
        """
        Initialize the GatekeeperServer.
        :param host: IP address or hostname of the gatekeeper server.
        :param port: Port on which the gatekeeper server listens.
        :param nodes: Dictionary of MySQL nodes in the cluster with their roles.
        :param trusted_hosts: List of IP addresses of trusted hosts.
        """
        self.host = host
        self.port = port
        self.nodes = nodes
        self.trusted_hosts = trusted_hosts
        self.slave_nodes = [node for key, node in nodes.items() if key != 'master']

    def start(self):
        """
        Start listening for incoming connections.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)

        while True:
            connection, client_address = sock.accept()
            if client_address[0] in self.trusted_hosts:
                threading.Thread(target=self.handle_client, args=(connection,)).start()
            else:
                print("Unauthorized access attempt from:", client_address[0])
                connection.close()

    def handle_client(self, connection):
        """
        Handle requests from a trusted client.
        :param connection: Client socket connection.
        """
        # Here, implement the logic to determine if the request is a read or write operation
        # For this example, let's randomly choose a node for demonstration purposes
        target_node = random.choice(list(self.nodes.values()))

        # Establish a connection to the chosen MySQL node
        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_sock.connect((target_node, 3306))

        # Forward requests and responses between client and MySQL node
        while True:
            data = connection.recv(1024)
            if data:
                # Send data to MySQL node
                target_sock.sendall(data)
                # Receive response from MySQL node
                response = target_sock.recv(1024)
                # Send response back to client
                connection.sendall(response)
            else:
                break

        # Close the connections
        connection.close()
        target_sock.close()

# Node IPs and their roles in the MySQL cluster
nodes = {
    'master': 'ip-172-31-22-6.ec2.internal',
    'node1': 'ip-172-31-22-7.ec2.internal',
    'node2': 'ip-172-31-22-8.ec2.internal',
    'node3': 'ip-172-31-22-9.ec2.internal'
}

# Trusted hosts IPs
trusted_hosts = ['172.31.22.9','172.31.22.9']

# Complementary functions

def get_default_vpc_id(ec2_client):
    # Retrieve the ID of the default Virtual Private Cloud (VPC)
    return ec2_client.describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')


# Main execution
if __name__ == "__main__":
    # Initialize AWS EC2 client and resource for interacting with AWS
    print("Initializing client and resource")
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    ec2_resource = boto3.resource("ec2", region_name="us-east-1")
    
    # Get the default VPC ID (function declared later) and create a security group
    print("Creating cluster security group")
    vpc_id = get_default_vpc_id(ec2_client)
    security_group = create_gatekeeper_security_group(ec2_client,"cluster_group",vpc_id)
    time.sleep(60) # Wait for the security group to be fully created
    # Get the security group ID
    security_group_id = security_group['GroupId']
    print("Security group created successfully")

    # Create instances for the cluster: one master node and three slave or data nodes.
    master = create_gatekeeper_instance(ec2_resource, "172.31.22.6", security_group_id, open('cluster_management_setup.sh').read(), "Master")
    slaves = [
        create_gatekeeper_instance(ec2_resource, "172.31.22.7", security_group_id, open('data_node.sh').read(), "Slave-1"),
        create_gatekeeper_instance(ec2_resource, "172.31.22.8", security_group_id, open('data_node.sh').read(), "Slave-2"),
        create_gatekeeper_instance(ec2_resource, "172.31.22.9", security_group_id, open('data_node.sh').read(), "Slave-3")
    ]

    print("Waiting for cluster instances to be ready")
    # Wait until all instances are fully operational.
    instances_ids = [master[0].id] + [node[0].id for node in slaves]
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=instances_ids)
    
    # Start the gatekeeper server
    gatekeeper = GatekeeperServer('172.31.22.6', 8000, nodes, trusted_hosts)
    gatekeeper.start()
