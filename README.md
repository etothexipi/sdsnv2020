# sdsnv2020
Create, provision, and version control AWS infrastructure to manage data pipelines effectively

- Local Laptop/Desktop

    - 1) Setup newsapi dev account 
        - https://newsapi.org/
        - Get API Key
                
    - 2) Setup AWS free-tier account
        - https://aws.amazon.com/free/
        - sign in to console
        - Set region to N. Virginia (us-east-1) [top right]
        
    - 3) Provision free-tier EC2 insance
        - https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LaunchInstanceWizard:
        - Select Ubuntu Server 20.04 LTS (HVM), SSD Volume Type [64-bit (x86)]
        - Select t2.micro for free or other size depending on your budget/needs
            - For the Intermediate and Advanced Branch we'll need at least a t2.medium
        - Go to 4. Add Storage
            - Increase size to 30GB to stay on free tier
        - Go to 6. Configure Security Group
            - Add rule for port range 8080-8888 
            - Add rule for port 80
            - Choose My IP as source for increased security.
                - If using VPN, you may need to enter the IP manually instead of using "My IP" to detect it
        - Review and Launch
        - Create new key pair -> Download it
        - Launch Instance
        
    - 4) Create S3 bucket
        - Services -> S3 -> Create bucket
        - Bucket Name = sdsnv2020-[yourcustomname]-intro
            - We'll use this naming convention later when building from code in Pulumi
        - Region = US East (N. Virginia)
        - Use all default settings Next->Next->Create
        
    - 5) SSH/PuTTY into EC2 instance
        - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html
        - When connecting from Windows laptop/desktop (see above guide for Mac/Linux laptops)
            - install PuTTY http://www.chiark.greenend.org.uk/~sgtatham/putty/
            - convert your .pem key in step 3) to .ppk using PuTTYgen
                - Open PuTTYgen (Key Generator)
                    - Load [yourkeyname].pem
                    - Save private key (without passphrase)
                        - Call it [yourkeyname].ppk
                    - Close
        - Go to AWS EC2 Consoler -> Instances -> select your instance
            - Copy Public IPv4 DNS
        - Open PuTTY
            - For Host Name = ubuntu@[paste IPv4 DNS] like..
                - ubuntu@ec2-54-132-52-156.compute-1.amazonaws.com
            - On left go to Connection
                - Set "Second between keepalives" to 60
            - On left go to Connection -> SSH -> Auth
                - Private key file for authentication = [pathtoyourkey]\[yourkeyname].ppk
            - Go back to Session [top left of Category:]
            - Name your Saved Sessions something -> click Save -> Open -> Yes (about fingerprint)
            
            
- EC2 Instance

    - 1) Install apt and python dependencies
        ```
        sudo apt update -y
        sudo apt install python3 -y
        sudo apt install python3-pip -y
        sudo apt install jq -y
        sudo apt-get install python3-dev python3-venv python3-wheel -y
        curl -fsSL https://get.pulumi.com | sh
        sudo apt install awscli -y
        ```
        
    - 2) Setup AWS CLI
        - Run:
            - aws configure
                - enter Access Key and Secret Key (top right of AWS console -> [your account name] -> My Security Credentials -> Access keys -> Create Access Key -> Show Access Key)
                - Download to safe place
            - Default region name: us-east-1
            - Default output format: *blank*
            
    - 3) Fork this repo to  your github account, then clone project repo and checkout "intro" branch
        ```
        git clone https://github.com/<your-github-account>/sdsnv2020
        cd sdsnv2020/
        git checkout intro
        ```
        
    - 4) Setup python virtual environment
        - (from sdsnv2020/ folder) run
            ```
            python3 -m venv venv/
            source venv/bin/activate
            pip install -r requirements.txt
            ```
            
    - 5) Setup shell environment variables
        - `nano ~/.bashrc` (or use vi if you're hardcore)
            - Add vars at bottom
            - `export S3BUCKETNAME=[your S3 bucket name]` like...
                - `export S3BUCKETNAME=sdsnv2020-<your-accountname>-intro`
            - `export NEWSAPI_KEY=[your news api key]`
        - In Intermediate and Advanced branches we'll pass this into the container automatically with Pulumi
        - Set basic options for python style (only if using vi editor). Google "vi commands" for help
            ```
            vi ~/.vimrc
                colorscheme koehler
                set tabstop=8 softtabstop=0 expandtab shiftwidth=2 smarttab
            ```
        - Run 
            `exit`
        - Then SSH back into ec2 to activate variables
        
    - 6) Play with sample pipeline
        ```
        cd ~/sdsnv2020/
        cat pull.py
        cat clean.py
        python pull.py 
        python clean.py 
        ```
        
    - 7) Setup cron to schedule pipelines
        - `crontab -e`
        - See https://crontab.guru/ for cron notation help
        - For every 10 minutes add this line to crontab file:
            `*/10 * * * * bash ~/sdsnv2020/run.sh`
