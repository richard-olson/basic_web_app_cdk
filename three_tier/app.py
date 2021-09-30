import aws_cdk
from aws_cdk import (
    Stack,
    Tags,
    Duration,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_secretsmanager as secret
)
from constructs import Construct
from .properties import app_config

linux_ami = ec2.AmazonLinuxImage(
    generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
    edition=ec2.AmazonLinuxEdition.STANDARD,
    virtualization=ec2.AmazonLinuxVirt.HVM,
    storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
)


class App(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Instance role created for access to EC2, SSM and the db_credential
        instance_role = iam.Role(
            self,
            app_config['iam_id'],
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal('ec2.amazonaws.com'),
                iam.ServicePrincipal('ssm.amazonaws.com')
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name
                (
                    'AmazonSSMFullAccess'
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name
                (
                    'AmazonEC2ReadOnlyAccess'
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name
                (
                    'AmazonRDSReadOnlyAccess'
                )
            ]
        )

        # Load Balancer
        alb = elb.ApplicationLoadBalancer(
            self,
            app_config['alb_id'],
            vpc=vpc,
            internet_facing=True,
            load_balancer_name=app_config['alb_name']
        )

        alb.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), app_config['alb_sg_description'])

        listener = alb.add_listener(app_config['alb_listener_id'],
                                    port=80,
                                    open=True)

        with open("./user_data/user_data.sh") as initial_user_data:
            for line in initial_user_data.read():
                for k, v in app_config.items():
                    user_data = user_data.replace(k, str(v))
                user_data = user_data.replace(
                    'alb_dns', alb.load_balancer_dns_name)

        # AutoScaleGroup
        self.asg = autoscaling.AutoScalingGroup(
            self,
            app_config['asg_id'],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE
            ),
            instance_type=ec2.InstanceType(
                instance_type_identifier=app_config['instance']
            ),
            role=instance_role,
            machine_image=linux_ami,
            key_name=app_config['keypair'],
            user_data=ec2.UserData.custom(user_data),
            min_capacity=app_config['asg_min_instances'],
            max_capacity=app_config['asg_max_instances'],

        )

        # Tag Instances with Environment and App name.
        # Note these tags are used to set configuration variables in Flask
        Tags.of(self.asg).add('Environment', app_config['environment'])
        Tags.of(self.asg).add('AppName', app_config['app_name'])

        # Allow access to ASG from ALB and set up as target
        listener.add_targets(
            app_config['alb_target_group'],
            port=80,
            targets=[self.asg],
            health_check=elb.HealthCheck(
                interval=Duration.seconds(app_config['health_interval']),
                healthy_threshold_count=app_config['health_threshold_count']
            )
        )

        self.asg.connections.allow_from(
            alb, ec2.Port.tcp(80), app_config['asg_sg_description'])

        # Scale up AutoScaleGroup based on CPU utilisation
        self.asg.scale_on_cpu_utilization(
            app_config['asg_scaling_policy_id'],
            target_utilization_percent=50,
            cooldown=Duration.seconds(app_config['asg_scale_out_cooldown'])
        )
        # Database Credentials added in app so that policy can
        # be created and applied to role
        self.db_credentials = secret.Secret(
            self,
            app_config['rds_secret_id'],
            secret_name=app_config['rds_secret_name'],
            generate_secret_string=secret.SecretStringGenerator(
                exclude_characters='/"@ '
            )
        )

        # Flask secret key
        self.flask_credentials = secret.Secret(
            self,
            app_config['flask_secret_id'],
            secret_name=app_config['flask_secret_name'],
            generate_secret_string=secret.SecretStringGenerator(
                exclude_characters='/"@ '
            )
        )

        self.db_credentials.grant_read(self.asg.role)
        self.flask_credentials.grant_read(self.asg.role)
