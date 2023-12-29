def create_standalone_security_group(ec2_client, sg_name, vpc_id):
    """
    Function that creates security group for standalone and assigns inbound rules
    :param ec2_client: The ec2 client that creates the security group
    :param sg_name: The name of the security group
    :param vpc_id: id of the vpc need to create security group
    :returns: the created security group
    """
    security_group = ec2_client.create_security_group(
        Description="MYSQL Standalone Security Group",
        GroupName=sg_name,
        VpcId=vpc_id
    )
    add_standalone_inbound_rules(ec2_client, security_group['GroupId'])
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

def add_standalone_inbound_rules(ec2_client, sg_id):
    """
    Function that assigns inbound rules to the standalone security group
    :param ec2_client: The ec2 client that will assign rules
    :param sg_id: Security group's id
    """

    inbound_rules = [
        {
            'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
        ]
    ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=inbound_rules)
    

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


def delete_security_group(ec2_client, sg_id):
    """
    Function that deletes the security group
    :param ec2_client: The ec2 client that will delete in teardown
    :param sg_id: Security group's id
    """
    ec2_client.delete_security_group(GroupId=sg_id)