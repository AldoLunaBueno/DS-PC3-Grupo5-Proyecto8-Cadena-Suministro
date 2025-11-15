output "registry_address" {
  description = "Dirección (host:port) del registro local simulado"
  value       = var.registry_address
}

output "registry_config_path" {
  description = "Ruta al archivo de configuración del registry"
  value       = local_file.registry_config.filename
}

output "builder_name" {
  description = "Nombre del builder local simulado"
  value       = var.builder_name
}

output "builder_config_path" {
  description = "Ruta al archivo de configuración del builder"
  value       = local_file.builder_config.filename
}

output "infra_status" {
  description = "Estado de la infraestructura simulada"
  value = {
    registry = {
      name    = var.registry_name
      address = var.registry_address
      status  = "active"
    }
    builder = {
      name   = var.builder_name
      status = "active"
    }
  }
}
