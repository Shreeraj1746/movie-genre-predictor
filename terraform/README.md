# Movie Genre Predictor Infrastructure

This directory contains the Terraform code to provision the infrastructure for the Movie Genre Predictor application on AWS.

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->

## Architecture

The infrastructure is organized as follows:

- **VPC**: Network isolation and security
- **EC2**: Application servers
- **S3**: Model and data storage
- **IAM**: Security permissions

## Deployment

To deploy the infrastructure:

1. Initialize Terraform:
   ```
   terraform init
   ```

2. Review the plan:
   ```
   terraform plan
   ```

3. Apply the changes:
   ```
   terraform apply
   ```

4. Generate documentation (optional):
   ```
   make terraform-docs
   ```
