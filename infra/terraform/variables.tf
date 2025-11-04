variable "docker_host" {
  description = "Socket o URL para conectar con el daemon de Docker"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "registry_container_name" {
  description = "Nombre para el contenedor del registro local"
  type        = string
  default     = "local_registry"
}

variable "builder_container_name" {
  description = "Nombre para el contenedor del constructor local"
  type        = string
  default     = "local_builder"
}

variable "registry_external_port" {
  description = "Puerto externo para el registro local"
  type        = number
  default     = 5000
}