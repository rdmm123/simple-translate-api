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

        function = aws_lambda.DockerImageFunction(
            self,
            "StApi",
            code=aws_lambda.DockerImageCode.from_image_asset(
                "..",
                file="functions/api/Dockerfile",
            ),
            timeout=Duration.seconds(60),
        )
        url = function.add_function_url(auth_type=aws_lambda.FunctionUrlAuthType.NONE)
        CfnOutput(self, "ApiFnName", value=function.function_name)
        CfnOutput(self, "ApiFnUrl", value=url.url)
        # bucket.grant_read_write(function)

        # function = aws_lambda.Function(
        #     self,
        #     "SimpleTranslateMessager",
        #     code=aws_lambda.Code.from_asset(""),
        #     runtime=aws_lambda.Runtime.PYTHON_3_13,
        #     handler="main.handler",
        # )
