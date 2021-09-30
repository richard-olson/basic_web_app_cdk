from aws_cdk import aws_secretsmanager as sm
from constructs import Construct


def create_secret(scope: Construct, my_id, name):
    secret = sm.Secret(
        scope,
        my_id,
        secret_name=name,
        generate_secret_string=sm.SecretStringGenerator(
            exclude_characters='/"@ '
        )
    )
    return secret
