from aws_cdk import aws_ssm as ssm
from constructs import Construct


def create_parm(scope: Construct, my_id, name, value):
    parm = ssm.StringParameter(
        scope,
        my_id,
        parameter_name=name,
        string_value=value
    )
    return parm
