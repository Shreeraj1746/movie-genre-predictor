terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "movie-genre-predictor"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# Security group for the EC2 instance
resource "aws_security_group" "movie_predictor_sg" {
  name        = "movie_predictor_sg"
  description = "Security group for Movie Genre Predictor"

  # Allow HTTP traffic
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTPS traffic
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH traffic
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  # Allow API traffic
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance (using t3.micro, which is free tier eligible)
resource "aws_instance" "movie_predictor_server" {
  ami                    = var.ami_id # Amazon Linux 2023 AMI
  instance_type          = "t3.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.movie_predictor_sg.id]

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 8
    delete_on_termination = true
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y git python3 python3-pip python3-venv

              # Setup the application directory
              mkdir -p /home/ec2-user/movie-genre-predictor
              cd /home/ec2-user/movie-genre-predictor

              # Clone the repository
              git clone https://github.com/${var.github_username}/movie-genre-predictor.git .

              # Setup Python environment
              python3 -m venv venv
              source venv/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt

              # Setup systemd service
              cat > /etc/systemd/system/movie-genre-predictor.service << 'EOL'
              [Unit]
              Description=Movie Genre Predictor FastAPI Service
              After=network.target

              [Service]
              User=ec2-user
              WorkingDirectory=/home/ec2-user/movie-genre-predictor
              ExecStart=/home/ec2-user/movie-genre-predictor/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
              Restart=always
              RestartSec=5

              [Install]
              WantedBy=multi-user.target
              EOL

              # Enable and start service
              sudo systemctl enable movie-genre-predictor.service
              sudo systemctl start movie-genre-predictor.service

              # Setup Nginx as reverse proxy (optional)
              sudo yum install -y nginx

              cat > /etc/nginx/conf.d/movie-predictor.conf << 'EOL'
              server {
                  listen 80;
                  server_name _;

                  location / {
                      proxy_pass http://localhost:8000;
                      proxy_set_header Host $host;
                      proxy_set_header X-Real-IP $remote_addr;
                  }
              }
              EOL

              sudo systemctl enable nginx
              sudo systemctl start nginx
              EOF

  tags = {
    Name = "MoviePredictorServer"
  }
}

# Elastic IP for the EC2 instance
resource "aws_eip" "movie_predictor_ip" {
  instance = aws_instance.movie_predictor_server.id
}
