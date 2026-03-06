locals {
  environment = "prod"
  name_prefix = "${var.REPO_NAME}-${local.environment}"  
  common_tags = {
    Environment = local.environment
    Project     = var.REPO_NAME
    Terraform   = "true"
  } 
  domain = "${var.DOMAIN}"
}

module "vpc" {
  source = "../../modules/vpc"
  
  name = local.name_prefix
  tags = local.common_tags
}

module "ec2" {
  source = "../../modules/ec2"
  
  name           = local.name_prefix
  type           = var.instance_type
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.public_subnet_ids
  SSH_KEY        = var.SSH_KEY
  SSH_KEY_PUB    = var.SSH_KEY_PUB
  ports          = var.allowed_ports
  domain         = local.domain
  REPO_NAME      = var.REPO_NAME
  FULL_REPO_NAME = var.FULL_REPO_NAME
  tags           = local.common_tags
  
  depends_on = [module.vpc]
}

# module "s3" {
#   source = "../../modules/s3"
#   name   = "${local.name_prefix}-upload"
# }

