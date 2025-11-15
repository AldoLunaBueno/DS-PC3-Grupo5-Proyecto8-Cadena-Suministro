#!/usr/bin/env bash
set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para imprimir mensajes con formato
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para validar la rama (opcional, puede omitirse en local)
validate_branch() {
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || echo "")
    
    if [ -z "$current_branch" ]; then
        log_warn "No se pudo detectar la rama actual. Continuando..."
        return 0
    fi
    
    log_info "Rama actual: $current_branch"
}

# Paso 1: Verificar que estamos en un repositorio Git
log_info "Paso 1: Verificando repositorio Git..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "No se detectó un repositorio Git. Este script debe ejecutarse desde la raíz del proyecto."
    exit 1
fi

# Paso 2: Escanear con Gitleaks
log_info "Paso 2: Escaneando secretos con Gitleaks..."
if command_exists gitleaks; then
    if gitleaks detect --no-git --source . --verbose; then
        log_info "Escaneo de secretos completado sin hallazgos"
    else
        log_error "Se detectaron secretos en el código. Revisa los resultados arriba."
        exit 1
    fi
else
    log_warn "Gitleaks no está instalado. Instalando..."
    if [ -f Makefile ]; then
        make install-gitleaks || {
            log_error "No se pudo instalar Gitleaks. Instálalo manualmente."
            exit 1
        }
        gitleaks detect --no-git --source . --verbose || {
            log_error "Se detectaron secretos en el código."
            exit 1
        }
    else
        log_error "No se encontró Makefile. Instala Gitleaks manualmente."
        exit 1
    fi
fi

# Paso 3: Instalar herramientas de infraestructura (Terraform, TFlint, tfsec)
log_info "Paso 3: Verificando herramientas de infraestructura..."

# Verificar Terraform
if ! command_exists terraform; then
    log_warn "Terraform no está instalado. Instalando..."
    if [ -f Makefile ]; then
        make install-infra-tools || {
            log_error "No se pudo instalar las herramientas de infraestructura."
            exit 1
        }
    else
        log_error "Terraform no está instalado. Instálalo manualmente."
        exit 1
    fi
else
    log_info "Terraform está instalado: $(terraform version | head -n1)"
fi

# Verificar tflint
if ! command_exists tflint; then
    log_warn "tflint no está instalado. Instalando..."
    if [ -f Makefile ]; then
        make install-infra-tools || {
            log_error "No se pudo instalar tflint."
            exit 1
        }
    else
        log_error "tflint no está instalado. Instálalo manualmente."
        exit 1
    fi
else
    log_info "tflint está instalado: $(tflint --version)"
fi

# Verificar trivy (usado en el Makefile)
if ! command_exists trivy; then
    log_warn "trivy no está instalado. Instalando..."
    if [ -f Makefile ]; then
        make install-infra-tools || {
            log_error "No se pudo instalar trivy."
            exit 1
        }
    else
        log_error "trivy no está instalado. Instálalo manualmente."
        exit 1
    fi
else
    log_info "trivy está instalado: $(trivy --version | head -n1)"
fi

# Paso 4: Preparar la infraestructura (terraform plan)
log_info "Paso 4: Preparando la infraestructura (terraform plan)..."
if [ -f Makefile ]; then
    if make tf-plan; then
        log_info "Plan de infraestructura generado correctamente"
    else
        log_error "Error al generar el plan de infraestructura"
        exit 1
    fi
else
    log_error "No se encontró Makefile. No se puede ejecutar tf-plan."
    exit 1
fi

# Paso 5: Validar infraestructura
log_info "Paso 5: Validando infraestructura..."
if [ -f Makefile ]; then
    if make tf-validate; then
        log_info "Validación de formato y sintaxis completada"
    else
        log_error "Error en la validación de formato o sintaxis"
        exit 1
    fi
    
    if make tf-check; then
        log_info "Checks de seguridad (tflint y trivy) completados"
    else
        log_error "Error en los checks de seguridad"
        exit 1
    fi
else
    log_error "No se encontró Makefile."
    exit 1
fi

# Paso 6: Verificar Python
log_info "Paso 6: Verificando Python..."
if ! command_exists python3; then
    log_error "Python 3 no está instalado. Instálalo antes de continuar."
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    log_info "$PYTHON_VERSION está instalado"
fi

# Paso 7: Preparar el entorno virtual
log_info "Paso 7: Preparando el entorno virtual..."
if [ -f Makefile ]; then
    if [ ! -d .venv ]; then
        log_info "Creando entorno virtual..."
        make install-env || {
            log_error "No se pudo crear el entorno virtual."
            exit 1
        }
    else
        log_info "Entorno virtual ya existe"
    fi
else
    log_error "No se encontró Makefile."
    exit 1
fi

# Paso 8: Validar el código (linting y formateo)
log_info "Paso 8: Validando código (linting y formateo)..."
if [ -f Makefile ]; then
    # En modo CI, FIX=false (solo verifica, no corrige)
    export CI=true
    if make lint-format; then
        log_info "Validación de código completada"
    else
        log_error "Error en la validación de código. Revisa los resultados arriba."
        exit 1
    fi
else
    log_error "No se encontró Makefile."
    exit 1
fi

# Paso 9: Ejecutar tests unitarios e integración
log_info "Paso 9: Ejecutando tests unitarios e integración..."
if [ -f Makefile ]; then
    if [ ! -d .venv ]; then
        log_error "El entorno virtual no existe. Debe ejecutarse 'make install-env' primero."
        exit 1
    fi
    
    if make test; then
        log_info "Tests completados exitosamente"
        
        # Verificar que se generaron los reportes de cobertura
        if [ -d reports/coverage ]; then
            log_info "Reportes de cobertura generados en reports/coverage/"
        else
            log_warn "No se encontraron reportes de cobertura (puede ser opcional)"
        fi
    else
        log_error "Los tests fallaron. Revisa los resultados arriba."
        exit 1
    fi
else
    log_error "No se encontró Makefile."
    exit 1
fi

# Paso 10: Generar SBOM
log_info "Paso 10: Generando SBOM..."
if [ -f supply/generate_sbom.py ]; then
    if python3 supply/generate_sbom.py; then
        if [ -f sbom.json ]; then
            log_info "SBOM generado correctamente: sbom.json"
        else
            log_error "El script se ejecutó pero no se generó sbom.json"
            exit 1
        fi
    else
        log_error "Error al generar el SBOM"
        exit 1
    fi
else
    log_error "No se encontró supply/generate_sbom.py"
    exit 1
fi

# Paso 11: Generar Dashboard de Seguridad
log_info "Paso 11: Generando Dashboard de Seguridad..."
if [ -f scripts/generate_dashboard.py ]; then
    if python3 scripts/generate_dashboard.py; then
        if [ -f dashboard.html ]; then
            log_info "Dashboard generado correctamente: dashboard.html"
        else
            log_warn "El script se ejecutó pero no se generó dashboard.html (puede ser opcional)"
        fi
    else
        log_warn "Error al generar el dashboard (puede ser opcional, continuando...)"
    fi
else
    log_warn "No se encontró scripts/generate_dashboard.py (puede ser opcional)"
fi