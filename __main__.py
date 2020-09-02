import pulumi
import json
import pulumi_docker as docker
import pulumi_aws as aws

# Job parameters
config = pulumi.Config()
env = config.require('ENV')
report_name = f'analytics-{env}'
region = config.require('region')
set_image = 'taps/fortis/'
set_family = 'taps-fortis'

# Get network info from config
vpc = aws.ec2.Vpc.get("vpc-ebd5a891", "vpc-ebd5a891")
subnetId = config.require('subnetId')
subnet = aws.ec2.get_subnet(id=subnetId)

# Create an AWS email identity
#jonathan = aws.ses.EmailIdentity("jonathan", email="jonathan.sims@protonmail.com")



# Create S3 bucket
# TODO fix error no module pulumi_aws.s3.BucketLifecycleRuleArgs
if env == 'dev':
    bucket = aws.s3.Bucket(report_name,
        acl="private",
        bucket=f'now-insurance-analytics-{env}',
        tags={'group': 'analytics', 'env': env},
    )

elif env == 'staging':
    bucket = aws.s3.Bucket(report_name,
        acl="private",
        bucket=f'now-insurance-analytics-{env}',
        tags={'group': 'analytics', 'env': env},
    )

elif env == 'production':
    bucket = aws.s3.Bucket(report_name,
        acl="private",
        bucket=f'now-insurance-analytics-{env}',
        tags={'group': 'analytics', 'env': env},
    )

else:
    raise ValueError('ENV variable in config not in (dev, staging, production)')
    quit()



# Create ECR repository
registry = aws.ecr.Repository(report_name,
    image_scanning_configuration={
        "scanOnPush": True,
    },
    tags={'group': 'analytics', 'env': env},
)

# Build Docker image
image_registry = pulumi.Output.all(registry.repository_url,
    aws.ecr.get_authorization_token().user_name,
    aws.ecr.get_authorization_token().password).apply(
        lambda args: docker.ImageRegistry(args[0], args[1], args[2])
    )

# Push to ECR
my_image = docker.Image(report_name,
    image_name=registry.repository_url.apply(
        lambda server: f'{server}:{env}'),
    build=docker.DockerBuild(context=f'./{set_image}'),
    registry=image_registry,
)

# Define containers as list of json
#image_name = pulumi.Output.concat(registry.repository_url, "-", env)
#image_name = '370076501934.dkr.ecr.us-east-1.amazonaws.com/analytics-staging-f42be2a:staging-d5bb7425398c1c917924ff56854792f30f85253a85ee42061bc27066fb43f0f7'


# Create container and task
task = aws.ecs.TaskDefinition(report_name,
    cpu="256",
    execution_role_arn="arn:aws:iam::370076501934:role/ecsTaskExecutionRole",
    family=set_family,
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=['FARGATE'],
    task_role_arn="arn:aws:iam::370076501934:role/AWSECSTaskRole",
    container_definitions=my_image.image_name.apply(lambda image: json.dumps([{
        "command": ["python", "run.py", env, "etothexipi/fortis/production"],
        "image": image,
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "analytics",
                "awslogs-region": region,
                "awslogs-stream-prefix": report_name
                }
            },
        "name": report_name,
    }])),
    tags={'group': 'analytics', 'env': env},
)


# Create cluster
cluster = aws.ecs.Cluster(report_name,
    capacity_providers=['FARGATE'],
    default_capacity_provider_strategies=[{'capacityProvider': 'FARGATE'}],
    tags={'group': 'analytics', 'env': env},
)

# Schedule tasks
event_rule = aws.cloudwatch.EventRule(report_name,
    schedule_expression="rate(5 minutes)",
    role_arn=task.execution_role_arn,
    is_enabled=True,
    tags={'group': 'analytics', 'env': env},
)

event_target = aws.cloudwatch.EventTarget(report_name,
    arn=cluster.arn,
    ecs_target={
        "TaskDefinitionArn": task.arn,
        "LaunchType": "FARGATE",
        "NetworkConfiguration": {
            "Subnets": [subnetId],
            "AssignPublicIp": True
        }
    },
    role_arn='arn:aws:iam::370076501934:role/ecsEventsRole',
    rule=event_rule.name,
)



