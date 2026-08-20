# terraform/outputs.tf
output "server_public_ip" {
  value       = aws_instance.converter_server.public_ip
  description = "Your EC2 public IP"
}

output "app_url" {
  value       = "http://${aws_instance.converter_server.public_ip}:30080"
  description = "Your application URL - open this in browser"
}

output "ssh_command" {
  value       = "ssh -i ~/.ssh/converter-key ubuntu@${aws_instance.converter_server.public_ip}"
  description = "Command to SSH into your server"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.media_bucket.bucket
  description = "Your S3 bucket name"
}
output "monitoring_server_ip" {
  value = aws_instance.monitoring_server.public_ip
}

output "grafana_url" {
  value = "http://${aws_instance.monitoring_server.public_ip}:3000"
}
