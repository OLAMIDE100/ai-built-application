############ Snake Game Development Environment Project  ##########################
export DATABASE_HOST=$(gcloud sql instances describe general-cluster --project nabuminds-test  --format='value(ipAddresses.[0].ipAddress)')
export TF_VAR_gcp_project_name="nabuminds-test"
export GOOGLE_APPLICATION_CREDENTIALS=/Users/adebimpe/Documents/keys/terraform_automation_test.json
export TF_VAR_snake_game_db_password=$(gcloud secrets versions access latest --secret="snake-game"  --project $TF_VAR_gcp_project_name | jq -r ".\"postgres-password\"" )
