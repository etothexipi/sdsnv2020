import json
import pulumi
import pulumi_aws as aws
import pulumi_docker as docker
from pulumi import export, ResourceOptions


# Script parameters
cpu_units = '1024'
mem_units = '2048'
service_count = 3
image_path = './model/' # relative path of Dockerfile to build and push
region = 'us-east-1'


# Config parameters
config = pulumi.Config()
stack = pulumi.get_stack()
project = pulumi.get_project()
default_vpc = aws.ec2.get_vpc(default=True)
default_vpc_subnets = aws.ec2.get_subnet_ids(vpc_id=default_vpc.id)


# Create log group
logs = aws.cloudwatch.LogGroup(project,
    tags={'group': project, 'stack': stack},
)


# Create S3 bucket for data and validations
bucket = aws.s3.Bucket(f'bucket-{project}-{stack}',
    acl='private',
    bucket=f'{project}-{stack}',
    tags={'group': project, 'stack': stack},
)


# Create ECR repository
registry = aws.ecr.Repository(f'ecr-repo-{project}-{stack}',
    image_scanning_configuration={
        'scanOnPush': True,
    },
    tags={'group': project, 'stack': stack},
)


# Build Docker image locally and push to ECR
image_registry = pulumi.Output.all(registry.repository_url,
    aws.ecr.get_authorization_token().user_name,
    aws.ecr.get_authorization_token().password).apply(
        lambda args: docker.ImageRegistry(args[0], args[1], args[2])
    )

image = docker.Image(f'image-{project}-{stack}',
    image_name=registry.repository_url.apply(
        lambda arg: f'{arg}:{stack}'),
    build=docker.DockerBuild(context=image_path),
    registry=image_registry,
)


# Create an ECS cluster to run a container-based service.
cluster = aws.ecs.Cluster(f'cluster-{project}-{stack}',
    tags={'group': project, 'stack': stack},
)


# Create a SecurityGroup that permits HTTP ingress and unrestricted egress.
group = aws.ec2.SecurityGroup(f'secgrp-{project}-{stack}',
	vpc_id=default_vpc.id,
	description='Enable HTTP access',
	ingress=[aws.ec2.SecurityGroupIngressArgs(
		protocol='tcp',
		from_port=80,
		to_port=80,
		cidr_blocks=['0.0.0.0/0'],
	)],
  	egress=[aws.ec2.SecurityGroupEgressArgs(
		protocol='-1',
		from_port=0,
		to_port=0,
		cidr_blocks=['0.0.0.0/0'],
	)],
    tags={'group': project, 'stack': stack},
)


# Create a load balancer to listen for HTTP traffic on port 80.
alb = aws.lb.LoadBalancer(f'lb-{project}-{stack}',
	security_groups=[group.id],
	subnets=default_vpc_subnets.ids,
    tags={'group': project, 'stack': stack},
)

atg = aws.lb.TargetGroup(f'tg-{project}-{stack}',
	port=80,
	protocol='HTTP',
	target_type='ip',
	vpc_id=default_vpc.id,
    tags={'group': project, 'stack': stack},
)

wl = aws.lb.Listener(f'listener-{project}-{stack}',
	load_balancer_arn=alb.arn,
	port=80,
	default_actions=[aws.lb.ListenerDefaultActionArgs(
		type='forward',
		target_group_arn=atg.arn,
	)],
)


# Create an IAM role that can be used by service's task.
role = aws.iam.Role('task-exec-role',
	assume_role_policy=json.dumps({
		'Version': '2008-10-17',
		'Statement': [{
			'Sid': '',
			'Effect': 'Allow',
			'Principal': {
				'Service': 'ecs-tasks.amazonaws.com'
			},
			'Action': 'sts:AssumeRole',
		}]
	}),
)

rpa = aws.iam.RolePolicyAttachment('task-exec-policy',
	role=role.name,
	policy_arn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy',
)


# Create task with two containers, flask app and model app
task = aws.ecs.TaskDefinition(f'task-{project}-{stack}',
    cpu=cpu_units,
    execution_role_arn=role.arn,
    family=f'task-{project}-{stack}',
    memory=mem_units,
    network_mode="awsvpc",
    requires_compatibilities=['FARGATE'],
    task_role_arn="arn:aws:iam::370076501934:role/AWSECSTaskRole",
    container_definitions=pulumi.Output.all(image.image_name, logs.name, region).apply(lambda args: json.dumps([
        # Bare nginx container listening 
        {
            'name': 'webapp',
            'command': ["ls", "-lah"],
            'image': 'nginx',
            'portMappings': [{
                'containerPort': 80,
                'hostPort': 80,
                'protocol': 'tcp'
            }],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": args[1],
                    "awslogs-region": args[2],
                    "awslogs-stream-prefix": f'webapp-{project}-{stack}',
                    }
                },
        },
        {
            "name": f'model',
            #"command": ["bash", "myscript.sh"],
            "command": ["touch", "blah.txt"],
            "image": args[0],
            "essential": False,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": project,
                    "awslogs-region": region,
                    "awslogs-stream-prefix": f'model-{project}-{stack}',
                    }
                },
        },
    ])),
    tags={'group': project, 'stack': stack},
)


service = aws.ecs.Service(f'service-{project}-{stack}',
	cluster=cluster.arn,
    desired_count=service_count,
    launch_type='FARGATE',
    task_definition=task.arn,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
		assign_public_ip=True,
		subnets=default_vpc_subnets.ids,
		security_groups=[group.id],
	),
    load_balancers=[aws.ecs.ServiceLoadBalancerArgs(
		target_group_arn=atg.arn,
		container_name='webapp',
		container_port=80,
	)],
    opts=ResourceOptions(depends_on=[wl]),
    tags={'group': project, 'stack': stack},
)


# Print DNS to stdout
export('url', alb.dns_name)
