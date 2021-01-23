# ECS Model Endpoint with Pulumi

Scaffold project to quickly and easily manage AWS infrastructure with python


### Setup Pulumi

`curl -fsSL https://get.pulumi.com | sh`

`sudo apt install python3-venv python3-pip`

`export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID> && export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>`


### Create sample project

`mkdir quickstart && cd quickstart && pulumi new aws-python`


### Move Jonathan's project code into quickstart

- TODO: sign up for Pulumi teams so users can share projects

`cp ../__main__.py .`

`cp ../requirements.txt .`

`source venv/bin/activate`

`pip install -r requirements.txt`

`deactivate`


### Preview and spin up or destroy build

`pulumi up`

`pulumi destroy`


### Resources

Official Fargate example
- https://github.com/pulumi/examples/blob/master/aws-py-fargate/__main__.py

Pulumi python AWS modules
- https://github.com/pulumi/pulumi-aws/tree/master/sdk/python/pulumi_aws

ECS task definition reference
- https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_TaskDefinition.html

ECS container definition reference
- https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html
