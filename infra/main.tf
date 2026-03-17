# 1. Provider Configuration
provider "google" {
  project = "qwiklabs-asl-01-964394115550"
  region  = "us-central1"
}

# 2. Enable Required APIs
variable "gcp_service_list" {
  description = "The list of apis necessary for the Gen Z Translator"
  type        = list(string)
  default = [
    "aiplatform.googleapis.com",
    "texttospeech.googleapis.com",
    "firestore.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com"
  ]
}

resource "google_project_service" "enabled_apis" {
  for_each = toset(var.gcp_service_list)
  project  = "qwiklabs-asl-01-964394115550"
  service  = each.key
}

# 3. Provision the Firestore Database
resource "google_firestore_database" "database" {
  project     = "qwiklabs-asl-01-964394115550"
  name        = "gen-x-gen-z-vocabulary"
  location_id = "us-central1"
  type        = "FIRESTORE_NATIVE"

  # Ensure APIs are enabled before creating the DB
  depends_on = [google_project_service.enabled_apis]
}

# 4. Create a Service Account for the Agents
resource "google_service_account" "agent_sa" {
  account_id   = "gen-z-translator-sa"
  display_name = "Service Account for Multi-Agent Translator"
}

# 5. Deploy to Cloud Run
resource "google_cloud_run_v2_service" "default" {
  name     = "no-cap-translator"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/qwiklabs-asl-01-964394115550/no-cap-translator:latest" # Assumes you've built the image
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
      env {
        name  = "PROJECT_ID"
        value = "qwiklabs-asl-01-964394115550"
      }
    }
    service_account = google_service_account.agent_sa.email
  }

  depends_on = [google_project_service.enabled_apis]
}

# 6. Make the Cloud Run Service Public
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}