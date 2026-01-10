#!/bin/bash

echo "Starting complete deployment process..."
# Source environment variables
source set_env_test.sh

export TF_VAR_image_tag=$(date +%Y%m%d%H%M%S)


# Step 1: Deploy infrastructure
echo "=== Step 1: Deploying Infrastructure ==="
echo 'yes' | terraform -chdir=infrastructure/terraform init  
echo 'yes' | terraform -chdir=infrastructure/terraform validate
echo 'yes' | terraform -chdir=infrastructure/terraform plan -out=tfplan
terraform -chdir=infrastructure/terraform show -json tfplan > infrastructure/terraform/tfplan.json
conftest test --policy policy infrastructure/terraform/tfplan.json --all-namespaces


read -p "ARE YOU OK WITH THE ABOVE PLAN AND wWANT TO CONTINUE? (yes/no): " choice

case "$choice" in
  yes|YES|Yes)
    echo "Continuing with the script..."
    
    
    terraform -chdir=infrastructure/terraform apply -auto-approve

    # Get cluster credentials
    echo "=== Getting cluster credentials ==="
    gcloud container clusters get-credentials general-cluster --region europe-west3 --project nabuminds-test

    # Step 2: Set up namespace
    echo "=== Step 2: Namespace setup ==="
    # Create the 'datagaps' namespace if it doesn't exist
    kubectl create namespace snake-game --dry-run=client -o yaml | kubectl apply -f -

    


    # Step 3: Deploy applications support
    echo "=== Step 3: Deploying Applications Support==="

   

    kubectl apply -f infrastructure/manifest/secrets/secrets.yaml -n snake-game
    kubectl apply  -f infrastructure/manifest/network/managed-cert.yaml -n snake-game
    kubectl apply  -f infrastructure/manifest/network/ingress.yaml -n snake-game
    



    

    # Step 4: Deploy applications
    echo "=== Step 4: Deploying Backend Applications ==="

    kubectl apply -f infrastructure/manifest/workloads/backend/configmap.yaml -n snake-game
    envsubst < infrastructure/manifest/workloads/backend/pre-backend-deployment.yaml > infrastructure/manifest/workloads/backend/backend-deployment.yaml
    kubectl apply -f infrastructure/manifest/workloads/backend/backend-deployment.yaml -n snake-game
    kubectl apply -f infrastructure/manifest/workloads/backend/backend-service.yaml -n snake-game



    echo "=== Step 4: Deploying Frontend Applications ==="
    envsubst < infrastructure/manifest/workloads/frontend/pre-frontend-deployment.yaml > infrastructure/manifest/workloads/frontend/frontend-deployment.yaml
    kubectl apply -f infrastructure/manifest/workloads/frontend/frontend-deployment.yaml -n snake-game
    kubectl apply -f infrastructure/manifest/workloads/frontend/frontend-service.yaml -n snake-game



    


 
 

    # Note: Kubernetes resources (ingress, service account, storage class, etc.) 
    # are managed by Terraform in main.tf using kubernetes_manifest resources

    echo "Complete deployment finished!"

    # Step 5: clean up applications yaml
    echo "=== Step 4: General cleanup ==="
    rm -rf infrastructure/manifest/workloads/backend/backend-deployment.yaml
    rm -rf infrastructure/manifest/workloads/frontend/frontend-deployment.yaml
 
    ;;
  no|NO|No)
    echo "Exiting script."
    exit 1
    ;;
  *)
    echo "Invalid input. Please type yes or no."
    exit 1
    ;;

esac