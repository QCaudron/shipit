/*====
Variables used across all modules
======*/
locals {
  production_availability_zones = ["us-west-2a", "us-west-2b"]
}

provider "aws" {
  region  = "${var.region}"
  profile = "${var.aws_profile}"
}

module "networking" {
  source               = "./modules/networking"
  environment          = "production"
  project_name        = "${var.project_name}"
  vpc_cidr             = "10.0.0.0/16"
  public_subnets_cidr  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets_cidr = ["10.0.10.0/24", "10.0.20.0/24"]
  region               = "${var.region}"
  availability_zones   = "${local.production_availability_zones}"
}

module "ecs" {
  source              = "./modules/ecs"
  environment         = "production"
  project_name        = "${var.project_name}"
  project_version     = "${var.project_version}"
  vpc_id              = "${module.networking.vpc_id}"
  availability_zones  = "${local.production_availability_zones}"
  subnets_ids         = ["${module.networking.private_subnets_id}"]
  public_subnet_ids   = ["${module.networking.public_subnets_id}"]
  security_groups_ids = [
    "${module.networking.security_groups_ids}"
  ]
}
