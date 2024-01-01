
def create_standalone_security_group(ec2_client, group_name, vpc_id):
    # Create a new security group in the specified VPC.
    # A security group acts like a firewall, controlling traffic to and from instances.
    security_group = ec2_client.create_security_group(
        Description="MYSQL Standalone Security Group",  # Description of the security group.
        GroupName=group_name,  # Name of the security group.
        VpcId=vpc_id  # ID of the VPC where the security group will be created.
    )

    # Define the rules for allowing incoming network traffic.
    # Here, we are setting up a rule to allow SSH (Secure Shell) access.
    inbound_rules = [
        {
            'IpProtocol': 'tcp',  # The protocol (tcp for SSH).
            'FromPort': 22,       # The starting port number (22 for SSH).
            'ToPort': 22,         # The ending port number (22 for SSH).
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allowed IP range (0.0.0.0/0 means from any IP).
        }
    ]

    # Apply the defined rules to the security group.
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group['GroupId'],  # The ID of the newly created security group.
        IpPermissions=inbound_rules  # The rules to apply.
    )

    # Return the created security group information.
    return security_group

def create_cluster_security_group(ec2_client, sg_name, vpc_id):
    """
    Function that creates security group for cluster and assigns inbound rules
    :param ec2_client: The ec2 client that creates the security group
    :param sg_name: The name of the security group
    :param vpc_id: id of the vpc need to create security group
    :returns: the created security group
    """
    security_group = ec2_client.create_security_group(
        Description="MYSQL Cluster Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    add_cluster_inbound_rules(ec2_client, security_group['GroupId'])
    return security_group

def create_proxy_security_group(ec2_client, sg_name, vpc_id):
    """
    Function that creates security group for the proxy and assigns inbound rules
    :param ec2_client: The ec2 client that creates the security group
    :param sg_name: The name of the security group
    :param vpc_id: id of the vpc need to create security group
    :returns: the created security group
    """
    security_group = ec2_client.create_security_group(
        Description="MYSQL Proxy Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    add_cluster_inbound_rules(ec2_client, security_group['GroupId'])
    return security_group
    

def add_cluster_inbound_rules(ec2_client, sg_id):
    """
    Function that assigns inbound rules to the cluster security group
    :param ec2_client: The ec2 client that will assign rules
    :param sg_id: Security group's id
    """

    inbound_rules = [
        {
            'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': '-1', 'FromPort': 1186, 'ToPort': 1186,
            'IpRanges': [{'CidrIp': '172.31.16.0/20'}]
        }
        ]
    ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=inbound_rules)

