
variable "gcp_project_name" {
  type = string
  default = "nabuminds-test"
}

variable "region" {
  type = string
  default = "europe-west3"
}


variable "solution" {
  type = string
  default = "snake-game"
}

variable "image_tag" {
  type    = string
  default = "10"
}

variable "snake_game_db_password" {
  type    = string
  default = ""
}