import os
import aws_cdk as cdk
from stacks.simple_translate_stack import SimpleTranslateStack

app = cdk.App()

SimpleTranslateStack(
    app, "SimpleTranslateStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
