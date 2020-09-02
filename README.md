# sdsnv2020
Create, provision, and version control AWS infrastructure to manage data pipelines effectively

### Server Setup 
#### Amazon Linux 2 EC2 (ami-0323c3dd2da7fb37d)
Install git
> `sudo yum install git`

Install python3
> `sudo yum install python3.x86_64`

Install visidata (awesome tabular data tool for terminal)
> `pip3 install --user visidata`

Install apache webserver
> `sudo yum install mod_wsgi.x86_64`

Install Docker 
> `sudo yum install docker.x86_64`

Pull/clone this repo
> `git clone https://github.com/etothexipi/sdsnv2020`

Install Pulumi and venv in repo root. 
> `curl -fsSL https://get.pulumi.com | sh`
> `cd ./sdsnv2020/`
> `python3 -m venv venv/`
> `source venv/bin/activate`
> `pip install -r requirements.txt`
> `deactivate`

 Setup aws config 
> `aws configure`

(development) Setup JupyterLab server for wrangling and exploratory analysis
> `sudo yum install gcc python-devel`

> `pip3 install --user jupyterlab`

> see: https://docs.aws.amazon.com/dlami/latest/devguide/setup-jupyter-config.html for remaining steps

(development) Running Docker daemon and give permission to Pulumi (ec2-user)
> `sudo dockerd &`
> `sudo setfacl --modify user:ec2-user:rw /var/run/docker.sock`

(development) Setup virtual environment within each project folder for local development. Simulates pip install inside container.
> `python3 -m venv venv/`
> `source venv/bin/activate`
> `pip install -r requirements.txt`
> `deactivate`

(development) Run/Update Pulumi stack, build/update containers, etc.
> `pulumi up`

