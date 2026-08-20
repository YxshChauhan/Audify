# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# SSH Key pair (you must create this manually first — see note below)
resource "aws_key_pair" "converter_key" {
  key_name   = "converter-key"
  public_key = file(var.public_key_path)
}

# Security group — open ports 22 (SSH), 80 (HTTP), 5000 (Flask), 30080 (NodePort)
resource "aws_security_group" "converter_sg" {
  name        = "converter-sg"
  description = "Allow web and SSH traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
  from_port   = 3000
  to_port     = 3000
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
}

# Fetch latest Ubuntu 22.04 AMI dynamically (avoids compatibility issues)
data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# EC2 instance — t3.micro is FREE TIER (recommended)
resource "aws_instance" "converter_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.converter_key.key_name
  vpc_security_group_ids = [aws_security_group.converter_sg.id]

  root_block_device {
    volume_size = 20   # 20GB free tier
    volume_type = "gp2"
  }

  tags = {
    Name = "video-converter-server"
  }
}

# S3 bucket for video + audio storage
resource "aws_s3_bucket" "media_bucket" {
  bucket        = var.bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_ownership_controls" "media_bucket" {
  bucket = aws_s3_bucket.media_bucket.id
  rule { object_ownership = "BucketOwnerPreferred" }
}
resource "aws_security_group" "monitoring_sg" {
  name        = "monitoring-sg"
  description = "Allow Grafana and SSH"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "monitoring_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.converter_key.key_name
  vpc_security_group_ids = [aws_security_group.monitoring_sg.id]

  root_block_device {
    volume_size = 8
    volume_type = "gp2"
  }

  tags = {
    Name = "grafana-monitoring-server"
  }
}
