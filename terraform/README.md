# Movie Genre Predictor Infrastructure

This directory contains the Terraform code to provision the infrastructure for the Movie Genre Predictor application on AWS.

<!-- BEGIN_TF_DOCS -->


## Usage

Basic usage of this module:

```hcl
module "example" {
  source = "path/to/module"

  # Required variables


  # Optional variables with default values

  # app_name = "movie-genre-predictor"

  # aws_profile = "default"

  # aws_region = "us-east-1"

  # environment = "test"

  # instance_type = "t2.micro"

  # key_name = null

  # public_subnets = [
  "10.0.1.0/24",
  "10.0.2.0/24"
]

  # vpc_cidr = "10.0.0.0/16"

}
```

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.0 |

## Providers

No providers.

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name of the application | `string` | `"movie-genre-predictor"` | no |
| <a name="input_aws_profile"></a> [aws\_profile](#input\_aws\_profile) | AWS profile to use for credentials | `string` | `"default"` | no |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS region to deploy to | `string` | `"us-east-1"` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (dev, test, prod) | `string` | `"test"` | no |
| <a name="input_instance_type"></a> [instance\_type](#input\_instance\_type) | EC2 instance type | `string` | `"t2.micro"` | no |
| <a name="input_key_name"></a> [key\_name](#input\_key\_name) | Name of the SSH keypair to use for EC2 instance | `string` | `null` | no |
| <a name="input_public_subnets"></a> [public\_subnets](#input\_public\_subnets) | CIDR blocks for the public subnets | `list(string)` | <pre>[<br/>  "10.0.1.0/24",<br/>  "10.0.2.0/24"<br/>]</pre> | no |
| <a name="input_vpc_cidr"></a> [vpc\_cidr](#input\_vpc\_cidr) | CIDR block for the VPC | `string` | `"10.0.0.0/16"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_endpoint"></a> [app\_endpoint](#output\_app\_endpoint) | The endpoint URL for the movie genre predictor API |
| <a name="output_aws_region"></a> [aws\_region](#output\_aws\_region) | The AWS region where resources are deployed |
| <a name="output_instance_id"></a> [instance\_id](#output\_instance\_id) | The ID of the EC2 instance |
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
