from aws_cdk import (
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_rds as rds,
)
from constructs import Construct


def create_database(scope: Construct, vpc, rds_config, db_credentials):
    database = rds.DatabaseCluster(
        scope,
        rds_config['id'],
        default_database_name=rds_config['name'],
        engine=rds.DatabaseClusterEngine.aurora_mysql(
            version=rds.AuroraMysqlEngineVersion.of(rds_config['engine'])
        ),
        storage_encrypted=True,
        instance_props=rds.InstanceProps(
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.ISOLATED
            ),
            instance_type=ec2.InstanceType(
                instance_type_identifier=rds_config['instance']
            )
        ),
        instances=rds_config['rds_num_instances'],
        deletion_protection=False,
        cloudwatch_logs_exports=["audit", "error", "general", "slowquery"],
        backup=rds.BackupProps(
            retention=Duration.days(rds_config['backup_retention'])
        ),
        credentials=rds.Credentials.from_password(
            username=rds_config['rds_username'],
            password=db_credentials.secret_value
        ),
        removal_policy=RemovalPolicy.DESTROY
    )

    return database
