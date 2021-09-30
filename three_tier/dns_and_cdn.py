from aws_cdk import (
    aws_cloudfront as cf,
    aws_cloudfront_origins as cfo,
    aws_route53 as r53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
)


def get_dns_zone_info(scope, domains, id, my_zone):
        # Create object that references my existing route53 domain
        # to pass to ACM for DNS validation of certificate
        zone = r53.HostedZone.from_hosted_zone_attributes(
            scope,
            id,
            zone_name=domains["parent"],
            hosted_zone_id=my_zone,
        )
        return zone


def create_certificate(scope, site_domain, id, zone):

        # Create a dns validated certificate for cloudfront alias
        certificate = acm.DnsValidatedCertificate(
            scope,
            id,
            hosted_zone=zone,
            region="us-east-1",
            domain_name=site_domain,
        )
        return certificate


def create_cloudfront_distribution(scope, alb, cf_config, certificate, site_domain):
        # Cloudfront Origin and distribution pointing to ALB
        origin = cfo.LoadBalancerV2Origin(
            alb, protocol_policy=cf.OriginProtocolPolicy.HTTP_ONLY
        )

        cf_cache_policy = cf.CachePolicy(
            scope,
            cf_config["cache_id"],
            cache_policy_name=cf_config["cache_policy_name"],
            query_string_behavior=cf.CacheQueryStringBehavior.all(),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        cloudfront = cf.Distribution(
            scope,
            cf_config["id"],
            default_behavior=cf.BehaviorOptions(
                origin=origin,
                cache_policy=cf_cache_policy,
                allowed_methods=cf.AllowedMethods.ALLOW_ALL
            ),
            certificate=certificate,
            domain_names=[site_domain],
        )
        return cloudfront


def create_dns_alias(scope, id, site_domain, zone, cloudfront):
        # Create DNS alias for cloudfront distribution
        r53_alias = r53.ARecord(
            scope,
            id,
            record_name=site_domain,
            zone=zone,
            target=r53.RecordTarget(alias_target=targets.CloudFrontTarget(cloudfront)),
        )
        return r53_alias
