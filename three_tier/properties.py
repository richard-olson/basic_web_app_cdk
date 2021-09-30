environment = "Production"
app_name = "MyApp"
region = "ap-southeast-2"
domains = {
    "parent": "example.com",
    "development": "dev",
    "production": "prod",
}


vpc_config = {
    "id": app_name + environment + "VPC",
    "cidr": "10.10.0.0/16",
    "subnet_mask": 24,
    "max_azs": 3,
    "nat_gateways": 1,
    "public_subnet_name": environment + "-Public-",
    "private_subnet_name": environment + "-Private-",
    "iso_subnet_name": environment + "-Database-",
}

app_config = {
    "instance": "c5.large",
    "iam_id": app_name + environment + "InstanceRole",
    "keypair": "example-keypair-name",
    "image_type": "amazon_linux",
    "alb_id": app_name + environment + "ALB",
    "alb_name": app_name + environment + "ALB",
    "alb_listener_id": app_name + environment + "_Listener_80",
    "alb_sg_description": "HTTP internet access to ALB",
    "alb_target_group": app_name + environment + "AutoScaleGroupTarget",
    "asg_id": app_name + environment + "AutoScaleGroup",
    "asg_sg_description": "HTTP access for ALB to App servers",
    "asg_min_instances": 3,
    "asg_max_instances": 6,
    "asg_scaling_policy_id": "CPUScale",
    "cpu_target": 50,
    "rds_secret_id": app_name + environment + "rds-secret",
    "rds_secret_name": "/" + app_name + "/" + environment + "/RDS-Secret",
    "flask_secret_id": app_name + environment + "flask-secret",
    "flask_secret_name": "/" + app_name + "/" + environment + "/Flask-Secret",
    "environment": environment,
    "app_name": app_name,
    "health_interval": 5,
    "health_threshold_count": 5,
    "health_timeout": 4,
    "unhealthy_threshold_count": 3,
    "asg_scale_out_cooldown": 300,
    "asg_warm_up_cooldown": 300,
    "target_group_deregistration": 300,
}

rds_config = {
    "id": app_name + environment + "Cluster",
    "name": app_name + environment + "Database",
    "engine": "5.7.mysql_aurora.2.10.0",
    "instance": "r6g.large",
    "rds_sg_description": "SQL access for app servers to RDS",
    "rds_num_instances": 3,
    "rds_username": "admin",
    "backup_retention": 10,
    "endpoint_parm_id": app_name + environment + "_rds_endpoint_parm",
    "endpoint_parm_name": "/" + app_name + "/" + environment + "/RDS-Endpoint",
    "environment": environment,
}

cw_config = {
    "name": app_name + "-" + environment + "-Dashboard",
    "id": app_name + environment + "dash",
    "region": region,
}

cf_config = {
    "my_dns_zone_id": "Z01234567EXAMPLEZONE",
    "id": app_name + environment + "-Dist",
    "cache_id": app_name + environment + "-Cache",
    "cert_id": app_name + environment + "-Cert",
    "r53_zone_id": app_name + environment + "r53zone",
    "r53_alias_id": app_name + environment + "r53alias",
    "name": app_name + "-" + environment + "-Distribution",
    "cache_policy_name": app_name + environment + "-CachePolicy",
}

waf_config = {
    "id": app_name + environment + "-wafacl",
    "name": app_name + "-" + environment + "-WAFACL",
    "cw_metric": app_name + "-" + environment + "-WAF-CloudFront"
}