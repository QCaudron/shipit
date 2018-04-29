locals {
    vm_user = "ubuntu"
}

provider "aws" {
    region = "us-west-2"
}

resource "aws_instance" "shipit_box" {

    ami = "ami-22741f5a"
    instance_type = "t2.micro"

    key_name = "${var.key_name}"

    provisioner "remote-exec" {
        inline = ["echo Successfully connected."]
        connection {
            user = "${local.vm_user}"
            private_key = "${file(var.private_key_path)}"
        }
    }

    root_block_device {
        volume_size = 30
    }

    tags {
        Name = "q_shipit"
    }
}
