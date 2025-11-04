# Proyecto 8. Cadena de Suministro (local)

Para el desarrollador:

Ejecuta `make install` para instalar los hooks de git y las dependencias del proyecto.

## Cómo aplicar IaC local (Issue 2)

Este repositorio incluye un stack Terraform mínimo en `infra/terraform` que levanta contenedores Docker para simular un *builder* y un *registry* local.

Requisitos previos:
- Docker disponible (en WSL usa el socket por defecto `unix:///var/run/docker.sock`).
- Terraform, tflint y tfsec instalados en tu entorno (o ejecutar desde CI que los provea).

Pasos rápidos:

1. Inicia en la carpeta del repo y valida el Terraform:

```bash
make tf-validate
```

2. Ejecuta checks de seguridad/linters para IaC:

```bash
make tf-check
```

3. Visualiza (o aplica) el plan:

```bash
make tf-plan
# si quieres aplicar:
cd infra/terraform && terraform apply
```

Notas:
- `tf-check` ejecuta `tflint` y `tfsec --severity HIGH`. Si `tfsec` detecta hallazgos de severidad HIGH, el target fallará. Ajusta las reglas en `infra/terraform/.tfsec.yml` o en `.tflint.hcl` según lo necesario.
- El stack crea un registry en `localhost:5000` y un contenedor `local_builder` que queda corriendo (alpine en bucle). Revisa `infra/terraform/main.tf` para detalles.

