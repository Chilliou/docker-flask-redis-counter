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

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/iwocs-app"
  retention_in_days = 7
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

# --- 4. LOAD BALANCER (ALB) ---
resource "aws_lb" "main" {
  name               = "iwocs-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets
}

resource "aws_lb_target_group" "app_tg" {
  name        = "iwocs-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"
  health_check {
    path = "/"
    matcher = "200"
  }
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# --- 5. CLUSTER ECS ---
resource "aws_ecs_cluster" "main" {
  name = "iwocs-cluster"
}

# Rôle IAM pour l'exécution des tâches
resource "aws_iam_role" "ecs_exec_role" {
  name = "iwocs-ecs-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_exec_policy" {
  role       = aws_iam_role.ecs_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Définition de la tâche (Le plan du conteneur)
resource "aws_ecs_task_definition" "app" {
  family                   = "iwocs-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_exec_role.arn
  task_role_arn            = aws_iam_role.ecs_exec_role.arn 

  container_definitions = jsonencode([
    # --- CONTENEUR 1 : TON APP FLASK ---
    {
      name      = "flask-app"
      image     = "${aws_ecr_repository.app_repo.repository_url}:latest"
      essential = true
      portMappings = [{
        containerPort = 5000
        hostPort      = 5000
      }]
      environment = [
        { name = "REDIS_HOST", value = "localhost" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name
          "awslogs-region"        = "eu-north-1" 
          "awslogs-stream-prefix" = "ecs"
        }
      }
    },
    
    # --- CONTENEUR 2 : REDIS (Le Sidecar) ---
    {
      name      = "redis"
      image     = "redis:alpine" # On prend l'image officielle légère
      essential = true
      portMappings = [{
        containerPort = 6379
        hostPort      = 6379
      }]
    }
  ])
}

# Le Service (Lance et maintient le conteneur)
resource "aws_ecs_service" "main" {
  name            = "iwocs-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.public_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "flask-app"
    container_port   = 5000
  }
}

# Output final
output "app_url" {
  value = "http://${aws_lb.main.dns_name}"
}