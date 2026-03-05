# Template repository for Backend deployment to AWS EC2

This repo has a pipeline that:
- Deploys AWS EC2 Instance with own VPC and static Elastic IP
- Installs Docker and dependencies, setups git connection
- Pulls the project repo and runs the Docker-Compose file.
- Deploys changes to the project on push

Resources are named by the GitHub repository name. Information about the current infrastructure state is stored in the terraform-tfstate bucket, so you can adjust some resources on the fly and deploy changes by running the `deploy infrastructure` action again. If you want to deploy code changes manually, run `deploy changes to dev` action.


## Usage

### Step 1: On the repo main page, choose "Use this template" - "Create a new repository".

![!\[alt text\](image-1.png)](pictures/image-1.png)

_For additional details, look through_ https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template

> Note: Please use only lowercase letters, numbers or dashes (-) for the repository name. 


### Step 2: Put your code into a new repository.

### Step 3. Generate the SSH key for SSH access and deployment purposes.

For Linux:

```sh
ssh-keygen -t rsa -b 4096 -C "id_rsa" -f id_rsa2 -N ""
```

For Windows:

```sh
ssh-keygen -t rsa -b 4096 -C "id_rsa" -f id_rsa2
```

### Step 4. Add the `Deploy key` to your repository and paste the content of the SSH public key *.pub there.

![!\[alt text\](image.png)](pictures/image.png)

### Step 5. Add repository secrets.

![!\[alt text\](image-3.png)](pictures/image-3.png)

```sh
SSH_KEY: The content of the private SSH key for SSH access to the server.
SSH_KEY_PUB: The content of the public SSH key *.pub.
ENV: The content of .env file for a project.
ENVIRONMENT: Project environment (`dev` or `prod`).
DOMAIN: The domain name for your backend.
AWS_ACCESS_KEY_ID: IAM access key for AWS API operations.
AWS_SECRET_ACCESS_KEY: The secret key paired with the access key.
AWS_REGION: The AWS region where resources will be created (e.g., us-east-1).
```

### Step 6: And run the `deploy infrastructure` Action.

![!\[alt text\](image-2.png)](pictures/image-2.png)

### Step 7: Finally, open your browser and check your project is alive using `http://your-instance-ip` or your domain (if present).

## Logging

To check that the deployment is successful, you can inspect the workflow logs. There you can find Docker Compose build logs and the first Docker containers' logs to make sure applications started or to see exact errors.

## Additional setup

### S3 Bucket config

If you need an S3 Bucket for your project, uncomment the following block in [terraform/environments/dev/main.tf](https://github.com/osyshyn/deploy-backend-to-ec2-template/blob/main/terraform/environments/dev/main.tf) and [terraform/environments/prod/main.tf](https://github.com/osyshyn/deploy-backend-to-ec2-template/blob/main/terraform/environments/prod/main.tf)

```sh
# module "s3" {
#   source = "../../modules/s3"
#   name   = "${local.name_prefix}-upload"
# }
```

### Web Sockets config

If you need to enable the Web Sockets config, uncomment the appropriate block for ws or socket.io in [terraform/modules/ec2/main.tf](https://github.com/osyshyn/deploy-backend-to-ec2-template/blob/main/terraform/modules/ec2/main.tf)

```sh
        # location /ws/ {
        #   proxy_pass http://127.0.0.1:3100;
        #   proxy_http_version 1.1;

        #   proxy_set_header Upgrade $http_upgrade;
        #   proxy_set_header Connection "upgrade";

        #   proxy_set_header Host $host;
        #   proxy_set_header X-Real-IP $remote_addr;
        #   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        #   proxy_set_header X-Forwarded-Proto $scheme;

        #   proxy_read_timeout 86400;
        #   proxy_send_timeout 86400;
        # }


        # location /socket.io/   {
        #       proxy_pass http://127.0.0.1:3100/socket.io/;
        #       proxy_http_version 1.1;
        #       proxy_set_header Upgrade $http_upgrade;
        #       proxy_set_header Connection "Upgrade";
        #       proxy_set_header Host $host;
        #       proxy_set_header X-Real-IP $remote_addr;
        #       proxy_set_header Authorization $http_authorization;
        # }
```

### Upload file size limit config

If you want to change the upload file size limit for NGINX, change those values in [terraform/modules/ec2/main.tf](https://github.com/osyshyn/deploy-backend-to-ec2-template/blob/main/terraform/modules/ec2/main.tf)

```sh
      types_hash_max_size 10240;
      client_max_body_size 10M;
```

### EC2 Instance Config

Also, you can edit variables in [terraform/environments/dev/terraform.tfvars](https://github.com/osyshyn/deploy-backend-to-ec2-template/blob/main/terraform/environments/dev/terraform.tfvars) or in [terraform/environments/prod/terraform.tfvars](https://github.com/osyshyn/deploy-backend-to-ec2-template/blob/main/terraform/environments/prod/terraform.tfvars) to adjust inbound ports or instance type

```sh
# EC2 Instance
ports   = ["22", "80", "443"] - Inbound ports for your instance
type    = "t4g.small" - Type of your instance
```


***For any questions, ping DevOps.
Happy coding)***