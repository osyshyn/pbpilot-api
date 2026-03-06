output "instance_id" {
  description = "ID of the EC2 instance"
  value       = module.ec2_instance[0].id
}

output "instance_elastic_ip" {
  description = "Public elastic ip"
  value       = [aws_eip.ip.public_ip]
}