variable "key_name" {
    default = "shipit"
}

variable "private_key_path" {
    default = "~/.ssh/shipit.pem"
}

variable "tags" {
  type = "map"
  default = {
    Repo = "https://github.com/startup-systems/terraform-ansible-example"
    Terraform = true
  }
}
