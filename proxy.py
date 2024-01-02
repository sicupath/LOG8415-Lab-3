import socket
import threading
import random
import ping3
import boto3
from ec2_instances import *
from security_groups import *
import time

class ProxyServer:
    def __init__(self, host, port, nodes):
        """
        Initializes the ProxyServer with given host, port, and a dictionary of nodes.
        :param host: The IP address or hostname of the proxy server.
        :param port: The port on which the proxy server listens.
        :param nodes: A dictionary of MySQL nodes in the cluster with their roles.
        """
        self.host = host
        self.port = port
        self.nodes = nodes
        # Extracting slave nodes for load balancing (excluding the master node).
        self.slave_nodes = [node for key, node in nodes.items() if key != 'master']

    def start(self):
        """
        Starts the proxy server to listen for incoming connections.
        """
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the server address
        server_address = (self.host, self.port)
        sock.bind(server_address)
        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Accept a new connection
            connection, client_address = sock.accept()
            # Handle the connection in a new thread
            threading.Thread(target=self.handle_client, args=(connection,)).start()

    def handle_client(self, connection):
        """
        Handles the client request by forwarding it to an appropriate MySQL node.
        :param connection: The client socket connection.
        """
        # Choose a node based on a strategy (customize here as needed)
        target_host, target_port = self.choose_node_customized()

        # Establish a connection to the chosen MySQL node
        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_sock.connect((target_host, target_port))

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

    def choose_node_direct_hit(self):
        """
        Direct Hit strategy: Always chooses the master node.
        :return: Tuple of (host, port) of the master node.
        """
        return self.nodes['master'], 3306

    def choose_node_random(self):
        """
        Random strategy: Randomly chooses one of the slave nodes.
        :return: Tuple of (host, port) of a randomly chosen slave node.
        """
        return random.choice(self.slave_nodes), 3306

    def choose_node_customized(self):
        """
        Customized strategy: Chooses the node with the lowest ping time.
        :return: Tuple of (host, port) of the slave node with the lowest ping time.
        """
        fastest_node = min(self.slave_nodes, key=lambda node: ping3.ping(node))
        return fastest_node, 3306

# Node IPs of the cluster and their roles in the MySQL cluster
nodes = {
    'master': 'ip-172-31-22-6.ec2.internal',
    'node1': 'ip-172-31-22-7.ec2.internal',
    'node2': 'ip-172-31-22-8.ec2.internal',
    'node3': 'ip-172-31-22-9.ec2.internal'
}

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
    security_group = create_cluster_security_group(ec2_client,"cluster_group",vpc_id)
    time.sleep(60) # Wait for the security group to be fully created
    # Get the security group ID
    security_group_id = security_group['GroupId']
    print("Security group created successfully")

    # Create instances for the cluster: one master node and three slave or data nodes.
    master = create_proxy_server_instance(ec2_resource, "172.31.22.6", security_group_id, open('cluster_management_setup.sh').read(), "Master")
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
    
    # Start the proxy server on the specified IP and port
    proxy = ProxyServer('0.0.0.0', 8000, nodes)
    proxy.start()
