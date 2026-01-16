terraform {
  required_providers {
    google = {
      version = "7.0.0"
    }
  }
}



terraform {
  backend "gcs" {
    bucket = "nabuminds_terraform-test"
    prefix = "snake-game/state"
  }
}

provider "google" {

  project = var.gcp_project_name
  region  = var.region
}


################################################################################################### DOMAIN CONFIGURATION ########################################################################################################
#####################################################################################################################################################################################################################

resource "google_compute_global_address" "snake-game" {
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
  name         = "${var.solution}-domian-address"
  project      = var.gcp_project_name
  labels       = { "solution" : var.solution }
}


resource "google_dns_record_set" "snake-game" {
  name    = "${var.solution}.nabuminds-test.app."
  type    = "A"
  ttl     = 300
  project = "nabuminds-test"

  managed_zone = "nabuminds-test-app"

  rrdatas = [google_compute_global_address.snake-game.address]

  depends_on = [google_compute_global_address.snake-game]
}



################################################################################################### FRONTEND AND BACKEND IMAGE CONFIGURATION CONFIGURATION ########################################################################################################
##############################################################################################################################################################################################################################################



resource "google_artifact_registry_repository" "snake-game" {
  location      = var.region
  repository_id = var.solution
  description   = "Docker repository for custom snake game images"
  format        = "DOCKER"
  labels        = { "solution" : var.solution }
}


resource "null_resource" "build_and_push_backend_image" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = <<EOT
              docker build  --platform linux/amd64 -t ${google_artifact_registry_repository.snake-game.location}-docker.pkg.dev/${var.gcp_project_name}/${google_artifact_registry_repository.snake-game.repository_id}/backend-image:${var.image_tag}   -f ../../backend/Dockerfile  ../../backend
              gcloud auth configure-docker ${google_artifact_registry_repository.snake-game.location}-docker.pkg.dev
              docker push ${google_artifact_registry_repository.snake-game.location}-docker.pkg.dev/${var.gcp_project_name}/${google_artifact_registry_repository.snake-game.repository_id}/backend-image:${var.image_tag}
            EOT
  }
  depends_on = [google_artifact_registry_repository.snake-game]
}

resource "null_resource" "build_and_push_frontend_image" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = <<EOT
              docker build  --platform linux/amd64 -t ${google_artifact_registry_repository.snake-game.location}-docker.pkg.dev/${var.gcp_project_name}/${google_artifact_registry_repository.snake-game.repository_id}/frontend-image:${var.image_tag}   -f ../../frontend/Dockerfile  ../../frontend
              gcloud auth configure-docker ${google_artifact_registry_repository.snake-game.location}-docker.pkg.dev
              docker push ${google_artifact_registry_repository.snake-game.location}-docker.pkg.dev/${var.gcp_project_name}/${google_artifact_registry_repository.snake-game.repository_id}/frontend-image:${var.image_tag}
            EOT
  }
  depends_on = [google_artifact_registry_repository.snake-game]
}






################################################################################################### NODE POOL CONFIGURATION ########################################################################################################
####################################################################################################################################################################################################################################


resource "google_container_node_pool" "snake-game" {
  cluster            = "general-cluster"
  initial_node_count = 1
  location           = var.region
  max_pods_per_node  = 110
  name               = "snake-game-pool"
  project            = var.gcp_project_name
  network_config {
    enable_private_nodes = true
  }
  autoscaling {
    location_policy      = "ANY"
    max_node_count       = 1
    min_node_count       = 0
    total_max_node_count = 0
    total_min_node_count = 0
  }
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  node_config {
    disk_size_gb      = 100
    disk_type         = "pd-ssd"
    image_type        = "COS_CONTAINERD"
    labels            = { "solution" : "snake-game", "pool" : "snake-game-pool" }
    local_ssd_count   = 0
    logging_variant   = "DEFAULT"
    machine_type      = "e2-standard-2"
    metadata = {
      disable-legacy-endpoints = "true"
    }
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    preemptible     = false
    resource_labels = {}
    service_account = "gke-workload@${var.gcp_project_name}.iam.gserviceaccount.com"
    spot            = true
    taint  {
             effect = "NO_SCHEDULE"
             key    = "gke-instance"
             value  = "snake-game"
  }
    tags            = ["airflow"]
    shielded_instance_config {
      enable_integrity_monitoring = true
      enable_secure_boot          = false
    }
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
    strategy        = "SURGE"
  }

  lifecycle {
    ignore_changes = [
      node_config[0].linux_node_config,
      node_config[0].resource_labels

    ]
  }

}



################################################################################################### DATABASE  CONFIGURATION ########################################################################################################
#####################################################################################################################################################################################################################




resource "google_sql_user" "snake-game" {
  name            = "snake-game"
  instance        = "general-cluster"
  password        = var.snake_game_db_password
  deletion_policy = "ABANDON"

}



resource "google_sql_database" "snake-game" {
  name            = "snake-game"
  instance        = "general-cluster"
  deletion_policy = "DELETE"

}

