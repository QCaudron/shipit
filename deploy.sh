cd terraform
terraform init
terraform apply -auto-approve

cd ../ansible
TF_STATE=../terraform/terraform.tfstate ansible-playbook "--inventory-file=$(which terraform-inventory)" provision.yml

echo "Finished !"

cd ../terraform
terraform output
