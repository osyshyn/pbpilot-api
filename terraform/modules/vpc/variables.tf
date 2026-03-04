variable "name" {
  type        = string
  description = "Resources name"
}

variable "cidr_block" {
  type        = string
  description = "CIDR block for VPC"
  default     = "10.0.0.0/16"
}

variable "tags" {
  type        = map(string)
  description = "Tags for resources"
  default     = {}
}
