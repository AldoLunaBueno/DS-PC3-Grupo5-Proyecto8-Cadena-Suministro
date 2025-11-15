variable "registry_name" {
  description = "Nombre para el registro local simulado"
  type        = string
  default     = "local_registry"
}

variable "registry_address" {
  description = "Dirección del registro local (host:port)"
  type        = string
  default     = "localhost:5000"
}

variable "registry_port" {
  description = "Puerto del registro local"
  type        = number
  default     = 5000
}

variable "builder_name" {
  description = "Nombre del constructor local simulado"
  type        = string
  default     = "local_builder"
}
