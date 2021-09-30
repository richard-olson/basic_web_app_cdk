from aws_cdk import Annotations, aws_cloudwatch as cw, Duration
from aws_cdk.aws_autoscaling import AutoScalingGroup
from constructs import Construct


def create_dashboard(scope: Construct, cfg, asg_name, tg_name, alb_name):

    widget_config = [
        {
            "title": "AutoScaleGroup CPU Utilisation",
            "left_y_axis": cw.YAxisProps(min=0),
            "left_annotations": [
                cw.HorizontalAnnotation(value=50, label="CPU Threshold")
            ],
            "left": [
                cw.Metric(
                    region=cfg["region"],
                    namespace="AWS/EC2",
                    metric_name="CPUUtilization",
                    period=Duration.seconds(10),
                    dimensions_map={"AutoScalingGroupName": asg_name},
                )
            ],
        },
        {
            "title": "AutoScaleGroup Instances",
            "left_y_axis": cw.YAxisProps(min=0, max=6),
            "left": [
                cw.Metric(
                    region=cfg["region"],
                    namespace="AWS/ApplicationELB",
                    metric_name="HealthyHostCount",
                    period=Duration.seconds(10),
                    dimensions_map={"TargetGroup": tg_name, "LoadBalancer": alb_name},
                )
            ],
        },
        {
            "title": "Application Response Time",
            "left_y_axis": cw.YAxisProps(min=0, max=0.25),
            "left": [
                cw.Metric(
                    region=cfg["region"],
                    namespace="AWS/ApplicationELB",
                    metric_name="TargetResponseTime",
                    period=Duration.seconds(10),
                    dimensions_map={"TargetGroup": tg_name, "LoadBalancer": alb_name},
                )
            ],
        },
        {
            "title": "Application Request Count",
            "left_y_axis": cw.YAxisProps(min=0),
            "left": [
                cw.Metric(
                    region=cfg["region"],
                    namespace="AWS/ApplicationELB",
                    metric_name="RequestCount",
                    period=Duration.seconds(60),
                    statistic="sum",
                    dimensions_map={"TargetGroup": tg_name, "LoadBalancer": alb_name},
                ),
                cw.Metric(
                    region=cfg["region"],
                    namespace="AWS/ApplicationELB",
                    metric_name="RequestCountPerTarget",
                    period=Duration.seconds(60),
                    statistic="sum",
                    dimensions_map={"TargetGroup": tg_name, "LoadBalancer": alb_name},
                ),
            ],
        },
    ]

    widget_list = []
    for config in widget_config:
        widget = cw.GraphWidget(
            height=5, width=12, **config
        )
        widget_list.append(widget)

    dashboard = cw.Dashboard(
        scope,
        cfg["id"],
        dashboard_name=cfg["name"],
        widgets=[widget_list],

    )
    return dashboard
