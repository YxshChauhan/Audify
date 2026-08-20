output "monitoring_server_ip" {
  value       = aws_instance.monitoring_server.public_ip
  description = "Grafana monitoring server IP"
}

output "grafana_url" {
  value       = "http://${aws_instance.monitoring_server.public_ip}:3000"
  description = "Grafana dashboard URL"
}
