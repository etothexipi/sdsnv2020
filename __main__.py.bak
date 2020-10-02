import pulumi
import json
import pulumi_docker as docker
import pulumi_aws as aws


# Stack parameters
config = pulumi.Config()
stack = pulumi.get_stack()
project = pulumi.get_project()
project_stack = f'{project}-{stack}'
region = config.require('region')


# Get network info from config
default_vpc = aws.ec2.get_vpc(default='true')
default_vpc_subnets = aws.ec2.get_subnet_ids(vpc_id=default_vpc.id)
securityGroup = config.require('securityGroup')


# Job parameters
DATE_PULLED = '2020-09-30'
QUERY_PULLED = 'cryptocurrency'


# Create S3 bucket depending on stack 
if stack == 'dev':
    bucket = aws.s3.Bucket(project_stack,
        acl='private',
        bucket=f'sdsnv2020-{stack}',
        tags={'group': 'sdsnv2020', 'stack': stack},
    )

elif stack == 'staging':
    bucket = aws.s3.Bucket(project_stack,
        acl='private',
        bucket=f'sdsnv2020-{stack}',
        tags={'group': 'sdsnv2020', 'stack': stack},
    )

elif stack == 'production':
    bucket = aws.s3.Bucket(project_stack,
        acl='private',
        bucket=f'sdsnv2020-{stack}',
        tags={'group': 'sdsnv2020', 'stack': stack},
    )

else:
    raise ValueError('stack in config not in (dev, staging, production)')
    quit()


# Create ECR repository
registry = aws.ecr.Repository(project_stack,
    image_scanning_configuration={
        'scanOnPush': True,
    },
    tags={'group': 'sdsnv2020', 'stack': stack},
)

# Build Docker image
image_registry = pulumi.Output.all(registry.repository_url,
    aws.ecr.get_authorization_token().user_name,
    aws.ecr.get_authorization_token().password).apply(
        lambda args: docker.ImageRegistry(args[0], args[1], args[2])
    )

# Push to ECR
image = docker.Image(project_stack,
    image_name=registry.repository_url.apply(
        lambda arg: f'{arg}:{stack}'),
    build=docker.DockerBuild(context=f'./app/'),
    registry=image_registry,
)


# Create container and task
task = aws.ecs.TaskDefinition(project_stack,
    cpu='256',
    execution_role_arn='arn:aws:iam::370076501934:role/ecsTaskExecutionRole',
    family=project_stack,
    memory='512',
    network_mode='awsvpc',
    requires_compatibilities=['FARGATE'],
    task_role_arn='arn:aws:iam::370076501934:role/AWSECSTaskRole',
    container_definitions=pulumi.Output.all(image.image_name, bucket.id).apply(
        lambda args: json.dumps([{
            'command': ['bash', 'run.sh'],
            'image': args[0],
            'environment':[
                { 'name': 'DATE_PULLED',  'value': f'{DATE_PULLED}'  },
                { 'name': 'QUERY_PULLED', 'value': f'{QUERY_PULLED}' },
                { 'name': 'S3BUCKETNAME', 'value': f'{args[1]}'  }
            ],
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': 'sdsnv2020',
                    'awslogs-region': region,
                    'awslogs-stream-prefix': project_stack
                    }
                },
            'name': project_stack,
    }])),
    tags={'group': 'sdsnv2020', 'stack': stack},
)


# Create cluster
cluster = aws.ecs.Cluster(project_stack,
    capacity_providers=['FARGATE'],
    default_capacity_provider_strategies=[{'capacityProvider': 'FARGATE'}],
    tags={'group': 'sdsnv2020', 'stack': stack},
)

# Schedule tasks
event_rule = aws.cloudwatch.EventRule(project_stack,
    schedule_expression='rate(5 minutes)',
    role_arn='arn:aws:iam::370076501934:role/ecsTaskExecutionRole',
    is_enabled=True,
    tags={'group': 'sdsnv2020', 'stack': stack},
)

event_target = aws.cloudwatch.EventTarget(project_stack,
    arn=cluster.arn,
    ecs_target={
        'TaskDefinitionArn': task.arn,
        'LaunchType': 'FARGATE',
        'NetworkConfiguration': {
            'Subnets': [default_vpc_subnets.id],
            'SecurityGroups': [securityGroup],
            'AssignPublicIp': True
        }
    },
    role_arn='arn:aws:iam::370076501934:role/ecsEventsRole',
    rule=event_rule.name,
)


