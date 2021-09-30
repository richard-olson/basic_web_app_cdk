# Three Tier Webapp

CDKv2 code which builds out infrastructure for a three tier web application.

![Diagram of AWS Architecture for three tier web application](https://github.com/malbertus/basic_web_app_cdk/doc/diagram.png "Architecture Diagram")

## Infrastructure

The following infrastructure will be built

- A VPC with the following subnets
  - Public for the Application Load Balancer and NAT Gateway
  - Private for the application instances
  - Isolated for the database instances
- Security groups with appropriate inbound permissions
- Outbound internet access for application instances to bootstrap
- An Application Load Balancer
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

- region
- my_dns_zone_id
- keypair

The following variables should be customised to suit your scenario

- app_name
- environment
- domains
- max_azs
- asg_min_instances
- asg_min_instances
- rds_num_instances

## Notes

- The DNS zone must be created outside of this CDK code, however the subdomains for the application are created with this code.
