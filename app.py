#!/usr/bin/env python3
import os
import aws_cdk as cdk
import three_tier.properties as props
from three_tier.main import ThreeTier

ACCOUNT = os.environ.get("CDK_DEFAULT_ACCOUNT", "unknown")
REGION = os.environ.get("CDK_DEFAULT_REGION", "unknown")

env = cdk.Environment(account=ACCOUNT, region=REGION)
app = cdk.App()

three_tier = ThreeTier(app, props.app_name + "-" + props.environment, env=env)

app.synth()
