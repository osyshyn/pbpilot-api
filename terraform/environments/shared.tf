# Shared configuration for both environments
# This file can be symlinked or copied to each environment directory

locals {
  # Common tags for all resources
  common_tags = {
    Project     = var.REPO_NAME
    ManagedBy   = "terraform"
    Environment = var.environment
  }
  
  # Common naming convention
  name_prefix = "${var.REPO_NAME}-${var.environment}"
}

# Common data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# Common outputs
output "environment" {
  description = "Current environment"
  value       = var.environment
}

output "region" {
  description = "AWS region"
  value       = data.aws_region.current.name
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "project_name" {
  description = "Project name"
  value       = var.REPO_NAME
}
