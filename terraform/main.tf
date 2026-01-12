terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.28.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1" # ⚠️ Vérifie ta région AWS Academy
}

# --- 1. RÉSEAU (VPC) ---
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "iwocs-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-north-1a", "eu-north-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  
  # Économie étudiant : Pas de NAT Gateway
  enable_nat_gateway = false
  enable_vpn_gateway = false
  map_public_ip_on_launch = true
}

# --- 2. REGISTRE D'IMAGES (ECR) ---
resource "aws_ecr_repository" "app_repo" {
  name = "iwocs-flask-app"
  force_delete = true
}

# --- 3. SÉCURITÉ ---
resource "aws_security_group" "alb_sg" {
  name        = "iwocs-lb-sg"
  vpc_id      = module.vpc.vpc_id
  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  name        = "iwocs-ecs-sg"
  vpc_id      = module.vpc.vpc_id
  ingress {
    protocol        = "tcp"
    from_port       = 5000
    to_port         = 5000
    security_groups = [aws_security_group.alb_sg.id]
  }
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}