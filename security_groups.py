
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

def create_cluster_security_group(ec2_client, group_name, vpc_id):
    # This function creates a new security group for a MySQL Cluster within a specified VPC (Virtual Private Cloud).

    # Create the security group with a description and a name within the specified VPC.
    security_group = ec2_client.create_security_group(
        Description="MYSQL Cluster Security Group",
        GroupName=group_name,
        VpcId=vpc_id
    )

    # Define inbound rules for the security group to control incoming network traffic.
    inbound_rules = [
        {
            # Allow SSH (Secure Shell) access over TCP protocol on port 22 from any IP address.
            'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            # Allow MySQL Cluster traffic on a custom port (1186) from a specific IP range.
            # This rule is specific to the cluster communication.
            'IpProtocol': '-1', 'FromPort': 1186, 'ToPort': 1186,
            'IpRanges': [{'CidrIp': '172.31.16.0/20'}]
        }
    ]

    # Apply the defined rules to the security group.
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group['GroupId'],
        IpPermissions=inbound_rules
    )

    # Return the created security group information.
    return security_group




