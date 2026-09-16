output "landing_bucket_name" {
  description = "Name of the S3 landing bucket"
  value       = aws_s3_bucket.landing.bucket
}

output "landing_bucket_arn" {
  description = "ARN of the S3 landing bucket"
  value       = aws_s3_bucket.landing.arn
}

output "pipeline_access_key_id" {
  description = "Access key ID for the pipeline IAM user"
  value       = aws_iam_access_key.pipeline.id
}

output "pipeline_secret_access_key" {
  description = "Secret access key for the pipeline IAM user"
  value       = aws_iam_access_key.pipeline.secret
  sensitive   = true
}
