resource "aws_s3_bucket" "app_data" {
  bucket = "${var.app_name}-${var.environment}-data-${random_id.suffix.hex}"

  tags = {
    Name        = "${var.app_name}-data-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_id" "suffix" {
  byte_length = 4
}
