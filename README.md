# Proyecto 8. Cadena de Suministro (local)

Este proyecto implementa una **cadena de suministro de software (software supply chain)** local que garantiza la seguridad y trazabilidad de las dependencias del proyecto mediante:

- **Generación automática de SBOM (Software Bill of Materials)** en formato CycloneDX 1.4
- **Validación de esquema** del SBOM generado
- **Política de allowlist** para controlar dependencias permitidas
- **Integración con Git hooks** para validaciones automáticas
- **Pipeline CI/CD** con gates de seguridad
- **Infraestructura como Código (IaC)** con Terraform para entornos locales

## Arquitectura

El flujo de la cadena de suministro sigue el siguiente proceso:

```
┌─────────┐
│  Push   │  Desarrollador hace push al repositorio
└────┬────┘
     │
     ▼
┌─────────┐
│  Hook   │  Git hooks (pre-commit) ejecutan validaciones:
│         │  • Generación de SBOM
│         │  • Validación de esquema
│         │  • Validación de allowlist
│         │  • Linting y formateo
└────┬────┘
     │
     ▼
┌─────────┐
│   CI    │  Pipeline CI/CD (GitHub Actions):
│         │  • Tests unitarios e integración
│         │  • Cobertura de código (≥90%)
│         │  • Análisis estático (SAST)
│         │  • Auditoría de dependencias
│         │  • Validación de IaC
└────┬────┘
     │
     ▼
┌─────────┐
│  Gate   │  Gates de seguridad:
│         │  • SBOM válido y actualizado
│         │  • Todas las dependencias en allowlist
│         │  • Tests pasando con cobertura suficiente
│         │  • Sin vulnerabilidades críticas
└─────────┘
```

### Componentes Principales

- **`supply/generate_sbom.py`**: Genera el SBOM desde `requirements.txt` en formato CycloneDX 1.4
- **`supply/validate_schema.py`**: Valida que el SBOM cumpla con el esquema definido
- **`supply/validate_allowlist.py`**: Verifica que todas las dependencias estén en `allowlist.json` con versiones correctas
- **`allowlist.json`**: Lista blanca de dependencias aprobadas con versiones específicas
- **`infra/terraform/`**: Stack Terraform para simular builder y registry locales

## Decisiones de Diseño

### Política de Allowlist

La política de allowlist es un mecanismo de seguridad que asegura que **todas las dependencias del proyecto han sido revisadas y aprobadas** antes de su inclusión. Esto previene la introducción no autorizada de paquetes maliciosos o no verificados en la cadena de suministro.

#### Características

- **Control de versiones**: Solo se permiten versiones específicas pre-aprobadas
- **Validación automática**: Se valida en cada commit mediante Git hooks
- **Firma SHA256**: El SBOM incluye una firma hash para detectar modificaciones no autorizadas
- **Validación estricta**: Cualquier dependencia no listada o con versión incorrecta bloquea el commit

#### Archivo `allowlist.json`

Define la lista de dependencias permitidas con sus versiones aprobadas:

```json
{
  "fastapi": "0.118.0",
  "pytest": "8.2.2",
  "pytest-cov": "5.0.0",
  ...
}
```

#### Flujo de Validación

1. Se genera el SBOM desde `requirements.txt`
2. Se extraen todas las dependencias del SBOM
3. Se compara cada dependencia contra `allowlist.json`
4. Se verifica que la versión coincida exactamente
5. Si alguna validación falla, el proceso se detiene

### Formato SBOM (CycloneDX 1.4)

El SBOM sigue el estándar **CycloneDX 1.4** en formato JSON. Incluye:

- Metadatos del proyecto (nombre, versión, timestamp)
- Lista completa de componentes/dependencias
- Hashes SHA256 para verificación de integridad

## Cómo correr

### Instalación inicial

Para configurar el proyecto por primera vez:

```bash
make install
```

Este comando:
- Crea el entorno virtual de Python (`.venv`)
- Instala todas las dependencias de `requirements.txt`
- Instala y configura pre-commit
- Configura los Git hooks locales

### Configurar Git hooks

Si ya tienes el entorno instalado y solo necesitas configurar los hooks:

```bash
make setup-hooks
```

Este comando configura Git para usar los hooks de pre-commit que ejecutan:
- Generación automática de SBOM
- Validación de esquema
- Validación de allowlist
- Linting y formateo de código

### Ejecutar tests

Para ejecutar las pruebas unitarias con cobertura:

```bash
make test
```

Este comando:
- Ejecuta `pytest` con cobertura del módulo `supply`
- Requiere al menos 90% de cobertura (`--cov-fail-under=90`)
- Genera reportes HTML en `reports/coverage/`

### Linting y formateo

Para ejecutar todos los linters y formatters:

```bash
make lint
```

Este comando ejecuta `pre-commit run --all-files` que incluye:
- **Black**: Formateo de código Python
- **Flake8**: Linting de código Python
- **Gitleaks**: Detección de secretos
- **Generate SBOM**: Generación automática del SBOM

### Otros comandos útiles

```bash
make help          # Muestra todos los targets disponibles
make clean         # Limpia el entorno
make security-scan # Ejecuta escaneo de secretos con Gitleaks
```

## Cómo aplicar IaC local

Este repositorio incluye un stack Terraform mínimo en `infra/terraform` que **simula** un *builder* y un *registry* local usando recursos locales de Terraform (sin requerir Docker). El IaC está diseñado para ser **idempotente** (0% drift entre planes consecutivos).

### Requisitos previos

- **Terraform** instalado en tu entorno (versión >= 1.3.0)
- **tflint** y **tfsec** instalados para validaciones de seguridad

**Nota**: Esta implementación simula la infraestructura mediante archivos de configuración locales y recursos `null_resource`, sin necesidad de Docker u otros servicios externos.

### Pasos para aplicar IaC

#### 1. Validar la configuración de Terraform

```bash
make tf-validate
```

Este comando ejecuta:
- `terraform fmt -check`: Verifica que el código esté formateado correctamente
- `terraform validate`: Valida la sintaxis y configuración de Terraform

**Nota**: Este comando debe ejecutarse antes de cualquier cambio para asegurar que el código cumple con los estándares de formato.

#### 2. Ejecutar checks de seguridad y linters

```bash
make tf-check
```

Este comando ejecuta:
- `tflint`: Linter de Terraform que verifica buenas prácticas y posibles errores
- `trivy`: Escáner de seguridad que detecta configuraciones inseguras

**Importante**: Este target **falla** si `trivy` detecta hallazgos de severidad **HIGH** o superior. El objetivo es mantener **0 hallazgos "High"** en el código. Si encuentras hallazgos, debes corregirlos antes de continuar.

#### 3. Visualizar el plan

```bash
make tf-plan
```

Este comando:
- Inicializa Terraform (`terraform init`) si es necesario
- Muestra el plan de ejecución (`terraform plan`)

**Idempotencia**: Si ejecutas `make tf-plan` dos veces consecutivas sin cambios, deberías obtener **0 cambios** (0% drift), confirmando que el IaC es idempotente.

#### 4. Aplicar la infraestructura

```bash
make tf-apply
```

Este comando aplica los cambios y crea:
- Archivos de configuración que simulan un registry local en `localhost:5000` (configurable mediante variables)
- Archivos de configuración que simulan un builder local
- Recursos `null_resource` que representan los procesos simulados

#### 5. Destruir la infraestructura

```bash
make tf-destroy
```

Este comando destruye todos los recursos creados por Terraform.

### Configuración de herramientas

El proyecto incluye archivos de configuración para las herramientas de validación:

- **`.tflint.hcl`**: Configuración de tflint con reglas habilitadas para documentación, versiones de providers, etc.
- **`.tfsec.yml`**: Configuración de tfsec que falla si encuentra hallazgos HIGH o CRITICAL

### Notas importantes

- Esta es una **simulación** de infraestructura: no se crean contenedores Docker reales, sino archivos de configuración y recursos locales que representan el builder y registry
- Los archivos de configuración se crean en `infra/terraform/.infra/` (este directorio está en `.gitignore`)
- El IaC utiliza `lifecycle` blocks y `triggers` en recursos `null_resource` para asegurar idempotencia y evitar recreaciones innecesarias
- Revisa `infra/terraform/main.tf` para detalles de la configuración
- Las variables se pueden configurar en `infra/terraform/variables.tf`
- Los outputs muestran las rutas a los archivos de configuración generados y el estado de la infraestructura simulada
