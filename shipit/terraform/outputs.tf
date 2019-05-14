output "alb_dns_name" {
  value = "${module.ecs.alb_dns_name}"
}

output "ecr_repository" {
  value = "${module.ecs.repository_url}"
}

output "project_version" {
  value = "${var.project_version}"
}

