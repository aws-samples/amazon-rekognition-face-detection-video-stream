#!/usr/bin/env python3

import aws_cdk as cdk

from iac.iac_stack import IacStack


app = cdk.App()
IacStack(app, "iac")

app.synth()
