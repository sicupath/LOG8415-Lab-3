
def create_standalone_instance(ec2_resource, security_group_id, subnet_id):
    # This function creates an EC2 instance (a virtual server) in AWS.

    # Specify the configuration for the new instance.
    instance_config = {
        'ImageId': "ami-0574da719dca65348",  # ID of the Amazon Machine Image (AMI) to use.
        'InstanceType': "t2.micro",  # Type of instance (t2.micro is a small, affordable type).
        'KeyName': "vockey",  # Name of the key pair for SSH access.
        'UserData': open('standalone.sh').read(),  # Script to run on instance initialization.
        'SubnetId': subnet_id,  # ID of the subnet where the instance will be created.
        'SecurityGroupIds': [security_group_id],  # ID of the security group to apply.
        'MaxCount': 1,  # Maximum number of instances to launch.
        'MinCount': 1,  # Minimum number of instances to launch.
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'MYSQL Standalone EC2 Instance'
                    },
                ]
            },
        ]
    }

    # Create the instance with the specified configuration.
    instance = ec2_resource.create_instances(**instance_config)

    # Return the created instance.
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
