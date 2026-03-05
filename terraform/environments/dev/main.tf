locals {
  environment = "dev"
  name_prefix = "${var.REPO_NAME}-${local.environment}"  
  common_tags = {
    Environment = local.environment
    Project     = var.REPO_NAME
    Terraform   = "true"
  } 
  domain = "${var.DOMAIN}"
}

# Use default VPC instead of creating a new one
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

module "ec2" {
  source = "../../modules/ec2"
  
  name           = local.name_prefix
  type           = var.instance_type
  vpc_id         = data.aws_vpc.default.id
  subnet_ids     = data.aws_subnets.default.ids
  SSH_KEY        = var.SSH_KEY
  SSH_KEY_PUB    = var.SSH_KEY_PUB
  ports          = var.allowed_ports
  domain         = local.domain
  REPO_NAME      = var.REPO_NAME
  FULL_REPO_NAME = var.FULL_REPO_NAME
  tags           = local.common_tags
}

# module "s3" {
#   source = "../../modules/s3"
#   name   = "${local.name_prefix}-upload"
# }

