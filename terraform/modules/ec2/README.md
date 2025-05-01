# EC2 Module

This module provisions EC2 instances for the Movie Genre Predictor application.

<!-- BEGIN_TF_DOCS -->


## Usage

Basic usage of this module:

```hcl
module "example" {
  source = "path/to/module"

  # Required variables

  app_name =

  environment =

  iam_role =

  instance_type =

  s3_bucket =

  subnet_id =

  vpc_id =


  # Optional variables with default values

  # key_name = null

  # user_data = null

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
| [aws_instance.app](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) | resource |
| [aws_security_group.app_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_ami.amazon_linux](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ami) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name of the application | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (dev, test, prod) | `string` | n/a | yes |
| <a name="input_iam_role"></a> [iam\_role](#input\_iam\_role) | Name of the IAM instance profile to attach to the instance | `string` | n/a | yes |
| <a name="input_instance_type"></a> [instance\_type](#input\_instance\_type) | EC2 instance type | `string` | n/a | yes |
| <a name="input_key_name"></a> [key\_name](#input\_key\_name) | Name of the SSH key pair to use for the EC2 instance | `string` | `null` | no |
| <a name="input_s3_bucket"></a> [s3\_bucket](#input\_s3\_bucket) | Name of the S3 bucket to use for application data | `string` | n/a | yes |
| <a name="input_subnet_id"></a> [subnet\_id](#input\_subnet\_id) | ID of the subnet to launch the instance in | `string` | n/a | yes |
| <a name="input_user_data"></a> [user\_data](#input\_user\_data) | User data script for EC2 instance | `string` | `null` | no |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | ID of the VPC | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_instance_id"></a> [instance\_id](#output\_instance\_id) | ID of the EC2 instance |
| <a name="output_public_ip"></a> [public\_ip](#output\_public\_ip) | Public IP address of the EC2 instance |
| <a name="output_security_group_id"></a> [security\_group\_id](#output\_security\_group\_id) | ID of the security group attached to the EC2 instance |
<!-- END_TF_DOCS -->

## Notes

- Ensure that the necessary security groups are configured
- The EC2 instances are configured with the application AMI
- Auto-scaling is enabled based on CPU utilization
