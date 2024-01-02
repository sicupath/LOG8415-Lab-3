
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


def create_cluster_instance(ec2_resource, ip_address, security_group_id, user_data, instance_name):
    # This function creates a single EC2 instance with specified configurations.

    # Define the configuration for the new EC2 instance.
    instance_config = {
        'ImageId': "ami-0574da719dca65348",  # ID of the Amazon Machine Image (AMI) to use.
        'InstanceType': "t2.micro",  # The type of instance (t2.micro is a small, affordable type).
        'KeyName': "vockey",  # Name of the SSH key pair for secure access to the instance.
        'UserData': user_data,  # Script to run when the instance starts (for initial setup).
        'PrivateIpAddress': ip_address,  # Private IP address assigned to the instance.
        'SubnetId': 'subnet-0e3b3bc7324035810',  # ID of the subnet in which to launch the instance.
        'SecurityGroupIds': [security_group_id],  # ID of the security group to associate with the instance.
        'MaxCount': 1,  # Maximum number of instances to launch (set to 1 for a single instance).
        'MinCount': 1,  # Minimum number of instances to launch (set to 1 to ensure creation of the instance).
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name  # Name tag for the instance.
                    },
                ]
            },
        ]
    }

    # Create the instance with the specified configuration.
    instance = ec2_resource.create_instances(**instance_config)

    # Return the created instance.
    return instance

def create_proxy_server_instance(ec2_resource, ip_address, security_group_id, user_data, instance_name):
    # This function creates a single EC2 instance for the proxy server, with the specified type

    # Define the configuration for the new EC2 instance.
    instance_config = {
        'ImageId': "ami-0574da719dca65348",  # ID of the Amazon Machine Image (AMI) to use.
        'InstanceType': "t2.large",  # The type of instance (t2.large for the server).
        'KeyName': "vockey",  # Name of the SSH key pair for secure access to the instance.
        'UserData': user_data,  # Script to run when the instance starts (for initial setup).
        'PrivateIpAddress': ip_address,  # Private IP address assigned to the instance.
        'SubnetId': 'subnet-0e3b3bc7324035810',  # ID of the subnet in which to launch the instance.
        'SecurityGroupIds': [security_group_id],  # ID of the security group to associate with the instance.
        'MaxCount': 1,  # Maximum number of instances to launch (set to 1 for a single instance).
        'MinCount': 1,  # Minimum number of instances to launch (set to 1 to ensure creation of the instance).
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name  # Name tag for the instance.
                    },
                ]
            },
        ]
    }

    # Create the instance with the specified configuration.
    instance = ec2_resource.create_instances(**instance_config)

    # Return the created instance.
    return instance

