data "aws_iam_policy_document" "pipeline_s3_access" {
  statement {
    sid    = "ListLandingBucket"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.landing.arn,
    ]
  }

  statement {
    sid    = "ReadWriteLandingObjects"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      "${aws_s3_bucket.landing.arn}/*",
    ]
  }
}

resource "aws_iam_policy" "pipeline_s3_access" {
  name        = "${var.project_name}-s3-access"
  description = "Least-privilege access to the ${var.project_name} landing bucket"
  policy      = data.aws_iam_policy_document.pipeline_s3_access.json

  tags = local.common_tags
}

# Dedicated service user for the pipeline
resource "aws_iam_user" "pipeline" {
  name = "${var.project_name}-pipeline"

  tags = local.common_tags
}

resource "aws_iam_user_policy_attachment" "pipeline" {
  user       = aws_iam_user.pipeline.name
  policy_arn = aws_iam_policy.pipeline_s3_access.arn
}

# Programmatic credentials for the service user.
resource "aws_iam_access_key" "pipeline" {
  user = aws_iam_user.pipeline.name
}
