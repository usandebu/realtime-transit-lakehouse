variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Project name, used as a prefix for resource names and tags"
  type        = string
  default     = "realtime-transit-lakehouse"
}

variable "environment" {
  description = "Deployment environment (dev, prod, ...)"
  type        = string
  default     = "dev"
}
