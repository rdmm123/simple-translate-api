from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_lambda,
    aws_ecr_assets as ecr_assets
)
from constructs import Construct

class SimpleTranslateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self, 'SimpleTranslateVideos',
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            # bucket_key_enabled=True,
            lifecycle_rules=[
                s3.LifecycleRule(expiration=Duration.days(30))
            ]
        )
        CfnOutput(self, "BucketNameOutput", value=bucket.bucket_name)

        docker_image = ecr_assets.DockerImageAsset(self, "SimpleTranslateImage")
        function = aws_lambda.Function(
            self,
            "SimpleTranslateApi",
            code=aws_lambda.DockerImageCode.from_image_asset(docker_image),
        )
        bucket.grant_read_write(function)