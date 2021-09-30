from constructs import Construct
from aws_cdk import aws_iam as iam


def create_role(scope: Construct, my_id):
    role = iam.Role(
        scope,
        my_id,
        assumed_by=iam.CompositePrincipal(
            iam.ServicePrincipal('ec2.amazonaws.com'),
            iam.ServicePrincipal('ssm.amazonaws.com')
        ),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonSSMFullAccess'
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonEC2ReadOnlyAccess'
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonRDSReadOnlyAccess'
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'CloudWatchReadOnlyAccess'
            )
        ]
    )
    return role
