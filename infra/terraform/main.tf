resource "local_file" "infra_directory" {
  content  = ""
  filename = "${path.module}/.infra/.gitkeep"

  lifecycle {
    create_before_destroy = true
  }
}

resource "local_file" "registry_config" {
  content = jsonencode({
    name        = var.registry_name
    address     = var.registry_address
    port        = var.registry_port
    type        = "local_registry"
    status      = "active"
    created_at  = timestamp()
    description = "Simulación de registry local para almacenar artefactos"
  })
  filename        = "${path.module}/.infra/registry.json"
  file_permission = "0644"

  depends_on = [local_file.infra_directory]

  lifecycle {
    create_before_destroy = true
  }
}

resource "local_file" "builder_config" {
  content = jsonencode({
    name        = var.builder_name
    type        = "local_builder"
    status      = "active"
    created_at  = timestamp()
    description = "Simulación de builder local para compilar artefactos"
    registry    = var.registry_address
  })
  filename        = "${path.module}/.infra/builder.json"
  file_permission = "0644"

  depends_on = [local_file.infra_directory]

  lifecycle {
    create_before_destroy = true
  }
}

resource "null_resource" "registry_simulator" {
  triggers = {
    config_hash = sha256(local_file.registry_config.content)
    name        = var.registry_name
    port        = var.registry_port
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "null_resource" "builder_simulator" {
  triggers = {
    config_hash = sha256(local_file.builder_config.content)
    name        = var.builder_name
    registry    = var.registry_address
  }

  depends_on = [null_resource.registry_simulator]

  lifecycle {
    create_before_destroy = true
  }
}
