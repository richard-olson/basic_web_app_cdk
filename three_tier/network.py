from constructs import Construct
import aws_cdk.aws_ec2 as ec2
from .properties import vpc_config


def create_network(scope: Construct):
    vpc = ec2.Vpc(
        scope,
        vpc_config["id"],
        cidr=vpc_config["cidr"],
        max_azs=vpc_config["max_azs"],
        nat_gateways=vpc_config["nat_gateways"],
        subnet_configuration=[
            ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.PUBLIC,
                name=vpc_config["public_subnet_name"],
                cidr_mask=vpc_config["subnet_mask"],
            ),
            ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.PRIVATE,
                name=vpc_config["private_subnet_name"],
                cidr_mask=vpc_config["subnet_mask"],
            ),
            ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.ISOLATED,
                name=vpc_config["iso_subnet_name"],
                cidr_mask=vpc_config["subnet_mask"],
            ),
        ],
    )
    return vpc
