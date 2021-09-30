from aws_cdk import aws_wafv2 as waf

managed_rules = [
    {
        "name": "AWSManagedRulesCommonRuleSet",
        "priority": 10,
        "override_action": "none",
        "excluded_rules": [],
    },
    {
        "name": "AWSManagedRulesAmazonIpReputationList",
        "priority": 20,
        "override_action": "none",
        "excluded_rules": [],
    },
    {
        "name": "AWSManagedRulesKnownBadInputsRuleSet",
        "priority": 30,
        "override_action": "none",
        "excluded_rules": [],
    },
    {
        "name": "AWSManagedRulesSQLiRuleSet",
        "priority": 40,
        "override_action": "none",
        "excluded_rules": [],
    },
    {
        "name": "AWSManagedRulesLinuxRuleSet",
        "priority": 50,
        "override_action": "none",
        "excluded_rules": [],
    },
    {
        "name": "AWSManagedRulesUnixRuleSet",
        "priority": 60,
        "override_action": "none",
        "excluded_rules": [],
    },
]


def make_rules(scope, list_of_rules={}):
    rules = list()
    for r in list_of_rules:
        rule = waf.CfnWebACL.RuleProperty(
            name=r["name"],
            priority=r["priority"],
            override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
            statement=waf.CfnWebACL.StatementProperty(
                managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                    name=r["name"], vendor_name="AWS", excluded_rules=[]
                )
            ),
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name=r["name"],
                sampled_requests_enabled=True,
            ),
        )
        rules.append(rule)


def create_waf(scope, cfg):

    acl = waf.CfnWebACL(
        scope,
        cfg["id"],
        scope="CLOUDFRONT",
        name=cfg["name"],
        default_action=waf.CfnWebACL.DefaultActionProperty(allow={}, block=None),
        visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
            cloud_watch_metrics_enabled=True,
            metric_name=cfg["cw_metric"],
            sampled_requests_enabled=True,
        ),
        rules=make_rules(scope, managed_rules),
    )

    return acl
