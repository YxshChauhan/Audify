# terraform/variables.tf
variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "public_key_path" {
  description = "Path to your SSH public key"
  default     = "~/.ssh/converter-key.pub"
}

variable "bucket_name" {
  description = "S3 bucket name - must be globally unique"
  default     = "video-audio-converter-yourname-2024"
}

variable "instance_type" {
  default = "t3.small"
}