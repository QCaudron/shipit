output "address" {
    value = "${aws_instance.shipit_box.public_ip}"
}

output "ssh" {
    value = "ssh ${local.vm_user}@${aws_instance.shipit_box.public_ip}"
}
