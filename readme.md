# Three Tier Webapp

CDKv2 code which builds out infrastructure for a three tier web application.

![Diagram of AWS Architecture for three tier web application](https://github.com/malbertus/basic_web_app_cdk/blob/main/doc/diagram.png "Architecture Diagram")

## Infrastructure

The following infrastructure will be built

- A VPC with the following subnets
  - Public for the Application Load Balancer and NAT Gateway
  - Private for the application instances
  - Isolated for the database instances
- Security groups with appropriate inbound permissions
- Outbound internet access for application instances to bootstrap
- An Application Load Balancer with a listener targeting the instances within the Auto Scale Group
- A single NAT gateway
- An EC2 Auto Scaling Group
  - Amazon Linux 2 instances
  - A user data script to bootstrap instances with a [basic web application](https://github.com/malbertus/basic_web_app) and Apache
  - An instance role providing appropriate permissions for the application
- Amazon RDS Aurora MySQL instances
  - Encryption enabled
  - Backups
  - Deletion protection removed (for ease of practice runs)
  - Endpoint URL propagated for use by the application instances
- Secrets Manager generated and stored passwords for the application and database
- Route53 DNS subdomain created
- CloudWatch dashboard to monitor CPU, requests per second, healthy instance and application response time
- HTTPS certificate for subdomain automatically signed with Route53 DNS validation
- CloudFront CDN
  - Using certificate for HTTPS
  - Enables all methods for web application functionality

## Outputs

The following outputs are produced by the CDK code

- RDS Endpoint name
- Application Load Balancer DNS name
- Cloudfront Distribution domain name
- Route53 domain name

## Configuration

Configuration variables are found in `three_tier/properties.py`.

The following variables need to be customised for your own environment

- **region:** Used to configure the region which CloudWatch metrics are gathered
- **my_dns_zone_id:** used by CDK to reference existing Route53 DNS zone
- **keypair:** ssh keypair used to access instances

The following variables should be customised to suit your scenario

- **app_name:** determines part of the name of the CloudFormation stack and the application itself
- **environment:** determines part of the name of the CloudFormation stack and the application itself. Also ties into domain name
- **domains:** needs root domain name of Route53 zone. Also uses the `environment` varible for sub domain creation; shortens production to 'prod' and development to 'dev' when creating sub domains.
- **max_azs:** default is 3 as nearly all regions have at least 3 available
- **asg_min_instances:** default is 3 to match the default number of availability zones
- **asg_max_instances:** default is 6
- **rds_num_instances:** default is 3 to match the default number of availability zones

## Notes

- The DNS zone must be created outside of this CDK code, however the subdomains for the application are created with this code.
- A single NAT gateway has been provisioned. This results in inter-AZ traffic flow for internet connectivity while the application instances bootstrap, however this was necessary to avoid using too many elastic IP addresses and hitting the service quota (5x Elastic IPs per region) if multiple deployments are created within the same region - for example, a development deployment and production deployment.
- A CDN policy has been created which enables caching. The [basic web application](https://github.com/malbertus/basic_web_app) has been built to pass headers disabling caching for dynamic pages, but the CDN should cache static files like images, javascript and css.
- It is recommended to conduct any web load testing (using tools such as [Locust](https://github.com/locustio/locust)) against the ALB domain name
