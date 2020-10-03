# sdsnv2020
Create, provision, and version control AWS infrastructure to create data pipelines 

### SDSNV2020 Intermediate Branch
- Go to EC2 dashboard -> select instance -> actions -> image -> create image
- select new AMI from banner pop-up or from Images on left menu
- create new instance from AMI
    - Need at least 4GB ram, choose desired. 
	- Note: stopping an instance stops incurring cost but it will change the DNS upon start which is kind of annoying
    - use "default" vpc and default security group, don't need to create new one if personal use
    - 
- Setup plumi, docker and docker-compose
```pip3 install --user visidata
curl -fsSL https://get.pulumi.com | sh
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update -y
apt-cache policy docker-ce
sudo apt install docker-ce -y
sudo apt install docker-compose -y
sudo addgroup --system docker
sudo adduser $USER docker
newgrp docker
```

- `cd sdsnv2020/`
- `git checkout intermediate`
- Note python code and requirements.txt moved to app/ subfolder. This is where it will be containerized and tested with it's own virtual environment
- `pulumi new aws-python --force`
- interactive menu use values
    - project: sdsnv2020 
    - stack name: dev
    - region: us-east-1
- Set stack region
- `pulumi config set region us-east-1`
- Set security group
- If following along, make sure you're only using the default security group that comes with your VPC
- `pulumi config set securityGroup [paste security group id like sg-b3af938c]`
- Set aws account id (top-right drop-down in aws web console)
- `pulumi config set account_id [your id no dashes] --secret`
- Save and encrypt our api key in Pulumi
- `pulumi config set NEWSAPI_KEY [paste key] --secret`
- Check that it was created properly and encrypted
    - `cat Pulumi.dev.yaml`
- This value will be called in our __main__.py pulumi build script and encrypted up until being injected into the infrastructure or containers
- replace default __main__.py with backup from repo
- ```cp __main__.py.bak __main__.py```
- add pulumi docker to pulumi virtual environment
- `echo pulumi_docker >> requirements.txt`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `deactivate`
- Note: the `pulumi up` command automatically activates the venv. Make sure the venv is deactivated before running `pulumi up` later
- Setup great expectations locally (on ec2 instance)
- Assume already created venv in app/ directory and installed requirements.txt
- `cd ~/sdsnv2020/app/`
- `source venv/bin/activate`
- `great_expectations init`
    - go through interactive menu
	- configure datasource
	    - 1. Files on a filesystem..
	    - 1. Pandas
	    - path to data 
		- ./
	    - data asset name
		- local_csv
	- Do not profile new expectations for data asset
- Run intro script if don't have newsapi-pull-....csv data set in app/ folder
    - `cd ~/sdsnv2020/app/`
    - `bash run.sh`
- Create great expectations suite
    - `great_expectations suite scaffold sdsnv2020`
	- Interactive options:
	    - 1. choose from a list...
	    - 1. newsapi-pull-2020...
	    - name: sdsnv2020
	- ctrl+c to shutdown jupyter notebook
	- note: scaffolding automatically generates some expectations for us based on the data
    - `deactivate`
- Spin up local (on ec2 instance) containers for great expecations data_docs and editor notebook`
    - `cd ~/sdsnv2020/app/great_expectations/`
    - `docker-compose up --build`
	- note: this will utilize docker-compose.yml and Dockerfile to build two containers
	- in the ssh terminal, copy the jupyter notebook token in the url
- In a browser open:
- http://[your ec2 dns]:8888
    - e.g. http://ec2-34-204-205-213.compute-1.amazonaws.com:8888/
- enter token to sign in 
    - Open the notebook -> work/uncommitted/scaffold_sdsnv2020.ipynb
	- The editor notebook will allow you to profile and create tests (expectations) for your data interactively. 
	- These notebooks are disposable.
	    - To save your changes, execute a particular expectation in a notebook cell and be sure to run the last cell which saves them. 
	    - To drop an expectation, do not run that cell and then execute the last cell
    - In top/main cell in batch_kwargs replace
	- `"path": "/home/ubuntu/sdsnv2020/app/great_expectations/../newsapi-pull-2020-10-02-cryptocurrency.csv"`
	    - with
	- `"path": "../newsapi-pull-2020-10-02-cryptocurrency.csv"`
	- in same cell put '../' in the data context path like
	    - context = ge.data_context.DataContext('../')
    - proceed to create simple expectations
	- open some new cells and use tab completion to look through expectations like:
	    - `batch.expect_column_values_to_not_be_null(column='title_polarity')`
	    - `batch.expect_column_values_to_be_between(column='description_polarity', min_value=-1.0, max_value=1.0)`
	    - `batch.expect_column_values_to_be_of_type(column='title', type_='object')`
	    - `batch.expect_column_[tab]....`
	- This is a great way to explore and get to know your data while also creating machine and human readable tests
	- execute final cell to save
	    - if error about permissions, may need to quite docker-compose and delete local_site from main ssh terminal like
		- `rm -r uncommitted/data_docs/local_site/`
	    - then run 
		- `source ~/sdsnv2020/app/venv/bin/activate`
		- `great_expectations docs build`
    - Check out data_docs website for human-readable results of the expectations
	- `docker-compose up --build`
	- http://[your ec2 dns]:80
	    - e.g. http://ec2-34-204-205-213.compute-1.amazonaws.com:80/
- go back to `cd ~/sdsnv2020/app/` and build the main container that we're gonna put into Fargate cluster
    - `docker build ./`
    - copy id if successfully built
    - Run docker container, manually passing environment variables that will be done automatically in pulumi
	- Note we defined s3bucket and newsapi key in ~/.bashrc in Intro branch and configured aws credentials too
	    - run `cat ~/.aws/credentials` to copy your access keys from
	
```
docker run --env S3BUCKETNAME=$S3BUCKETNAME \
	--env AWS_ACCESS_KEY_ID=[your access key id] \
    --env AWS_SECRET_ACCESS_KEY=[your secret access key] \
    --env NEWSAPI_KEY=$NEWSAPI_KEY
```
- If you need to debug python or run.sh be sure to rebuild container each time to apply. We don't use volume mounts cause it's too hard to keep track of what won't be mounted in ECS Fargate cluster. Unless you want to setup and EFS share drive and mount to ECS and your EC2.
    
- Setup ECS roles for containers
    - iam
	- create role 'ecsTaskExecutionRole'  and attach
	    - AmazonECSTaskExecutionRolePolicy
	- create 'ecsEventsRole' and attach 
	    - AmazonEC2ContainerServiceEventsRole
	- create 'AWSECSTaskRole' and attach
	    - SecretsManagerReadWrite
	    - AWSLambdaFullAccess
	    - AmazonEC2ContainerServiceFullAccess
	- 
- once complete, ready to deploy
- run `pulumi up` from repo home directory `~/sdsnv2020/`
        
