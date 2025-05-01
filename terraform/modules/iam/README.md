# IAM Module

This module provisions IAM roles and policies for the Movie Genre Predictor application.

<!-- BEGIN_TF_DOCS -->


## Usage

Basic usage of this module:

```hcl
module "example" {
  source = "path/to/module"

  # Required variables

  app_name =

  environment =

  s3_bucket =


  # Optional variables with default values

}
```

## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_iam_instance_profile.ec2_profile](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_instance_profile) | resource |
| [aws_iam_role.ec2_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.s3_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name of the application | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (dev, test, prod) | `string` | n/a | yes |
| <a name="input_s3_bucket"></a> [s3\_bucket](#input\_s3\_bucket) | Name of the S3 bucket to grant access to | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_ec2_profile_name"></a> [ec2\_profile\_name](#output\_ec2\_profile\_name) | Name of the EC2 instance profile |
| <a name="output_ec2_role_arn"></a> [ec2\_role\_arn](#output\_ec2\_role\_arn) | ARN of the EC2 IAM role |
| <a name="output_ec2_role_name"></a> [ec2\_role\_name](#output\_ec2\_role\_name) | Name of the EC2 IAM role |
<!-- END_TF_DOCS -->

## Notes

- Follows the principle of least privilege
- Includes roles for EC2 instances and Lambda functions
- Provides policies for S3 bucket access and CloudWatch logging
