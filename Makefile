SHELL := /bin/bash
.ONESHELL:
.PHONY: help install install-hooks lint-format test deps-audit scan-secrets ci-local tf-validate tf-plan tf-check tf-apply tf-destroy clean
BIN = .venv/bin

# Detecta si el entorno es CI (GitHub Actions)
CI ?= false
BIN ?= .

# Si no es CI, se asume entorno local: FIX=true
ifeq ($(CI),true)
  FIX := false
else
  FIX := true
endif

help: ## Describe uso de cada target
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: install-hooks install-env install-gitleaks ## Instala dependencias y configura el entorno

install-infra-tools:
	@sudo apt update
	@sudo snap install trivy
	@sudo snap install tflint

install-env:
	@python3 -m venv .venv
	@sudo $(BIN)/pip install -r requirements.txt

install-gitleaks:
	@sudo apt update
	@GITLEAKS_VERSION=$$(curl -s "https://api.github.com/repos/gitleaks/gitleaks/releases/latest" | grep -Po '"tag_name": "v\K[0-9.]+')
	@wget -qO gitleaks.tar.gz "https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_$${GITLEAKS_VERSION}_linux_x64.tar.gz"
	@sudo tar xf gitleaks.tar.gz -C /usr/local/bin gitleaks
	@rm -rf gitleaks.tar.gz

install-hooks: ## Configura Git para usar nuestros hooks locales
	git config core.hooksPath .githooks/
	chmod +x .githooks/*

security-scan: ## Ejecuta escaneo de secretos con Gitleaks
	@gitleaks detect --no-git --source . --verbose

tf-plan: ## Inicializa la infraestructura y muestra el plan
	@cd infra/terraform
	@terraform init && terraform plan

tf-apply: ## Aplica la infraestructura con terraform apply
	@cd infra/terraform
	@terraform apply

tf-destroy: ## Destruye la infraestructura con terraform destroy
	@cd infra/terraform
	@terraform destroy

tf-validate: ## Ejecuta el formateo y validaciones de la infraestructura
	@cd infra/terraform
	@terraform fmt -check && terraform validate

tf-check: ## Ejecuta tflint y trivy (analizadores de infraestructura)
	@cd infra/terraform
	@tflint && trivy config .

lint-format: ## Ejecuta linters y formatters (auto-fix localmente)
ifeq ($(FIX),true)
	@echo "Ejecutando Ruff en modo auto-fix (local)"
	@$(BIN)/ruff check . --fix
	@$(BIN)/ruff format .
else
	@echo "Ejecutando Ruff en modo verificación (CI)"
	@$(BIN)/ruff check .
	@$(BIN)/ruff format --check .
endif

test: ## Ejecuta pruebas unitarias e integración
	@if [ ! -d .venv ]; then \
		echo "Error: entorno virtual .venv no encontrado. Ejecute 'make install' primero."; \
		exit 1; \
	fi
	$(BIN)/pytest tests/unit/ -v --cov=supply --cov-report=term-missing --cov-report=html:reports/coverage --cov-fail-under=90 --cov-config=.coveragerc

deps-audit: ## Escanea dependencias en busca de vulnerabilidades
	@echo "TODO: Implementar pip-audit -r requirements.txt"

ci-local: ## Ejecuta el pipeline de CI completo localmente
	@echo "TODO: Esto debe llamar a un script 'scripts/ci-local.sh'"
	@echo "TODO: El script 'ci-local.sh' debe validar la rama y luego ejecutar make lint, test, sast, etc."

clean:
	@sudo rm -rf .venv