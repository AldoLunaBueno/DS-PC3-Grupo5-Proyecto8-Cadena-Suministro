config {
  force = false
}

# Asegura que Terraform tenga versión
rule "terraform_required_version" {
  enabled = true
}

# Para detectar recursos no usados
rule "terraform_unused_declarations" {
  enabled = true
}

# Asegura que los modulos tengan recurso y version
rule "terraform_module_pinned_source" {
  enabled = true
  style = "semver"
}

# Asegura que los providers tengan versión
rule "terraform_required_providers" {
  enabled = true
}

# Variables deben estar documentadas
rule "terraform_documented_variables" {
  enabled = true
}

# Outputs deben estar documentadas
rule "terraform_documented_outputs" {
  enabled = true
}