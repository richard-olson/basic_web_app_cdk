from aws_cdk import (
    CfnOutput,
    Stack,
    Tags,
    Duration,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_autoscaling as autoscaling,
)
from constructs import Construct

from .network import create_network
from .image import create_image
from .iam import create_role
from .userdata import create_user_data
from .properties import *
from .rds import create_database
from .secret import create_secret
from .parameters import create_parm
from .cloudwatch import create_dashboard
from .waf import create_waf
from .dns_and_cdn import (
    get_dns_zone_info,
    create_certificate,
    create_cloudfront_distribution,
    create_dns_alias,
)


class ThreeTier(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Network
        vpc = create_network(self)

        # Amazon Linux image for use in AutoScaleGroup
        image = create_image(app_config["image_type"])

        # Instance role created for access to EC2, SSM and the db_credential
        instance_role = create_role(self, app_config["iam_id"])

        # Create Load Balancer
        alb = elb.ApplicationLoadBalancer(
            self,
            app_config["alb_id"],
            vpc=vpc,
            internet_facing=True,
            load_balancer_name=app_config["alb_name"],
        )

        # Create user data script with application
        # configuration and load balancer DNS
        user_data = create_user_data(app_config, alb.load_balancer_dns_name)

        # AutoScaleGroup
        asg = autoscaling.AutoScalingGroup(
            self,
            app_config["asg_id"],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            instance_type=ec2.InstanceType(
                instance_type_identifier=app_config["instance"]
            ),
            role=instance_role,
            machine_image=image,
            key_name=app_config["keypair"],
            user_data=ec2.UserData.custom(user_data),
            min_capacity=app_config["asg_min_instances"],
            max_capacity=app_config["asg_max_instances"],
            cooldown=Duration.seconds(app_config["asg_warm_up_cooldown"]),
            group_metrics=[autoscaling.GroupMetrics.all()],
            health_check=autoscaling.HealthCheck.elb(grace=Duration.seconds(300)),
        )

        # Tag Instances with Environment and App name.
        # Note these tags are used to set configuration variables in Flask
        Tags.of(asg).add("Environment", app_config["environment"])
        Tags.of(asg).add("AppName", app_config["app_name"])

        # Scale up AutoScaleGroup based on CPU utilisation
        asg.scale_on_cpu_utilization(
            app_config["asg_scaling_policy_id"],
            target_utilization_percent=app_config["cpu_target"],
            cooldown=Duration.seconds(app_config["asg_scale_out_cooldown"]),
        )

        # Database Credentials and website secret key
        db_credentials = create_secret(
            self, app_config["rds_secret_id"], app_config["rds_secret_name"]
        )
        flask_credentials = create_secret(
            self, app_config["flask_secret_id"], app_config["flask_secret_name"]
        )

        # Allow ASG instances access to generated secrets
        db_credentials.grant_read(instance_role)
        flask_credentials.grant_read(instance_role)

        # Create Aurora Database
        rds = create_database(self, vpc, rds_config, db_credentials)

        # Create parameter with endpoint to enable application to find database
        db_endpoint = create_parm(
            self,
            rds_config["endpoint_parm_id"],
            rds_config["endpoint_parm_name"],
            rds.cluster_endpoint.hostname,
        )

        listener = alb.add_listener(app_config["alb_listener_id"], port=80, open=True)

        target_group = listener.add_targets(
            app_config["alb_target_group"],
            port=80,
            targets=[asg],
            health_check=elb.HealthCheck(
                interval=Duration.seconds(app_config["health_interval"]),
                healthy_threshold_count=app_config["health_threshold_count"],
                unhealthy_threshold_count=app_config["unhealthy_threshold_count"],
                timeout=Duration.seconds(app_config["health_timeout"]),
                path="/health",
            ),
            deregistration_delay=Duration.seconds(
                app_config["target_group_deregistration"]
            ),
        )

        # Connectivity between services
        # Internet access to ALB
        alb.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), app_config["alb_sg_description"]
        )

        # Allow access to ASG from ALB
        asg.connections.allow_from(
            alb, ec2.Port.tcp(80), app_config["asg_sg_description"]
        )

        # Allow access from AutoScalingGroup to new database cluster
        for asg_sg in asg.connections.security_groups:
            rds.connections.allow_default_port_from(
                asg_sg, rds_config["rds_sg_description"]
            )

        # Cloudwatch Dashboard
        cw_dash = create_dashboard(
            self,
            cw_config,
            asg.auto_scaling_group_name,
            target_group.target_group_full_name,
            alb.load_balancer_full_name,
        )

        # Define site domain name based on environment defined in properties
        dns_zone = get_dns_zone_info(
            self, domains, cf_config["r53_zone_id"], cf_config["my_dns_zone_id"]
        )

        # Custom URL prefix based on environment name
        # defined in properties
        site_domain = (domains[environment.lower()] + "." + domains["parent"]).lower()

        # Create certificate with DNS validation of domain ownership
        acm = create_certificate(self, site_domain, cf_config["cert_id"], dns_zone)

        # Create Cloudfront Distribution
        cdn = create_cloudfront_distribution(self, alb, cf_config, acm, site_domain)

        # Create route53 alias that links DNS zone and new Cloudfront distribution
        r53_alias = create_dns_alias(
            self, cf_config["r53_alias_id"], site_domain, dns_zone, cdn
        )

        # Needs to be created in different stack pointing to us-east-1
        # waf = create_waf(
        #     self,
        #     waf_config
        # )

        # Outputs to CLI
        CfnOutput(self, "RDS-Endpoint", value=rds.cluster_endpoint.hostname)
        CfnOutput(self, "ALB-DNS", value=alb.load_balancer_dns_name)
        CfnOutput(self, "CF-Domain-Name", value=cdn.domain_name)
        CfnOutput(self, "Route53", value=r53_alias.domain_name)
