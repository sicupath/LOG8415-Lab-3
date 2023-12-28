# Create t2.micro instance for the standalone MYSQL instance
def create_standalone_instance(ec2, securityGroup, subnet_id):
    """
    Function that creates t2.micro instance for the standalone MYSQL instance
    :param ec2_client: The ec2 client that creates the instance
    :param securityGroup: The id of the security group
    :param subnet_id: The subnet id where the instance will be
    :returns: the created instance
    """
    instance = ec2.create_instances(
        ImageId="ami-0574da719dca65348",
        InstanceType="t2.micro",
        KeyName="vockey",
        UserData=open('standalone_setup.sh').read(),
        SubnetId=subnet_id,
        SecurityGroupIds=[
            securityGroup
        ],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MYSQL-Standalone'
                },
            ]
        },
        ]
        )

    return instance


# Create t2.micro instances for the cluster
def create_cluster_instance(ec2, ip_address, securityGroup, userdata, instance_name, subnet_id):
    """
    Function that creates t2.micro instance for the  MYSQL cluster instances
    :param ec2_client: The ec2 client that creates the instance
    :param ip_address: The private ip address for the instance
    :param securityGroup: The id of the security group
    :param userdata: The specified userdata (master or slave) to configure instance on launch
    :param instance_name: The name of the instance
    :param subnet_id: The subnet id where the instance will be
    :returns: the created instance
    """
    instance = ec2.create_instances(
        ImageId="ami-0574da719dca65348",
        InstanceType="t2.micro",
        KeyName="vockey",
        UserData=userdata,
        PrivateIpAddress=ip_address,
        SubnetId=subnet_id,
        SecurityGroupIds=[
            securityGroup
        ],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': instance_name
                },
            ]
        },
        ]
        )

    return instance


# Create t2.large instance for the proxy
def create_proxy_instance(ec2, ip_address, securityGroup, subnet_id):
    """
    Function that creates t2.large instance for the proxy
    :param ec2_client: The ec2 client that creates the instance
    :param ip_address: The private ip address for the instance
    :param securityGroup: The id of the security group
    :param subnet_id: The subnet id where the instance will be
    :returns: the created instance
    """
    instance = ec2.create_instances(
        ImageId="ami-0574da719dca65348",
        InstanceType="t2.large",
        KeyName="vockey",
        UserData=open('proxy_setup.sh').read(),
        PrivateIpAddress=ip_address,
        SubnetId=subnet_id,
        SecurityGroupIds=[
            securityGroup
        ],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': "proxy"
                },
            ]
        },
        ]
        )

    return instance


# This function is defined to terminate the instance.
def terminate_instance(client, instanceId):
    """
    Function that terminate instance from given instance id
    :param client: The ec2 client that will delete the instance
    :param instanceId: The id of the instance to delete
    """
    print('terminating instance:')
    print(instanceId)
    client.terminate_instances(InstanceIds=(instanceId))