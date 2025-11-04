resource "docker_network" "iac_local_net" {
  name = "iac_local_net"
}

resource "docker_image" "registry" {
  name = "registry:2"
}

resource "docker_container" "registry" {
  name  = var.registry_container_name
  image = docker_image.registry.name

  ports {
    internal = 5000
    external = var.registry_external_port
  }

  networks_advanced {
    name = docker_network.iac_local_net.name
  }

  restart = "always"
}

resource "docker_image" "builder" {
  name = "alpine:3.18"
}

resource "docker_container" "builder" {
  name    = var.builder_container_name
  image   = docker_image.builder.name
  command = ["sh", "-c", "while true; do sleep 3600; done"]

  networks_advanced {
    name = docker_network.iac_local_net.name
  }

  restart = "no"
}