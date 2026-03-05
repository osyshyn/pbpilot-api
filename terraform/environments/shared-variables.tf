# Shared variables for both environments
# This file can be symlinked or copied to each environment directory

variable "environment" {
  type        = string
  description = "Environment name (dev, prod, staging, etc.)"
}

variable "AWS_REGION" {
  type        = string
  description = "AWS region for resources"
  default     = "us-east-1"
}

variable "SSH_KEY" {
  type        = string
  description = "Private SSH key for EC2 instance"
  sensitive   = true
}

variable "SSH_KEY_PUB" {
  type        = string
  description = "Public SSH key for EC2 instance"
}

variable "allowed_ports" {
  type        = list(string)
  description = "Ports to allow in security group"
  default     = ["22", "80", "443"]
}

variable "domain" {
  type        = string
  description = "Domain name for the application"
}

variable "REPO_NAME" {
  type        = string
  description = "Repository name"
}

variable "FULL_REPO_NAME" {
  type        = string
  description = "Full repository name (owner/repo)"
}
