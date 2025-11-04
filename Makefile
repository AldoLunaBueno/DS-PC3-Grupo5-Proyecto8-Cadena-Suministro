SHELL := /bin/bash
.ONESHELL:
.PHONY: help install install-hooks lint test sast deps-audit scan-secrets ci-local tf-validate tf-plan tf-check tf-apply tf-destroy

help: ## Describe uso de cada target
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: install-hooks ## Instala dependencias y configura el entorno
	@echo "TODO: Crear entorno virtual .venv"
	@echo "TODO: Instalar dependencias de Python"
	@echo "TODO: Instalar herramientas no-python (gitleaks, tflint, tfsec)"

install-hooks: ## Configura Git para usar nuestros hooks locales
	git config core.hooksPath .githooks/
	chmod +x .githooks/*

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

tf-check: ## Ejecuta tflint y tfsec (analizadores de infraestructura)
	@cd infra/terraform
	@tflint && tfsec .

lint: ## Ejecuta todos los linters
	@echo "TODO: Implementar lints"

test: ## Ejecuta pruebas unitarias e integración
	@echo "TODO: Implementar pytest"

sast: ## Ejecuta todo el análisis SAST
	@echo "Análisis SAST completados."

deps-audit: ## Escanea dependencias en busca de vulnerabilidades
	@echo "TODO: Implementar pip-audit -r requirements.txt"

scan-secrets: ## Escanea secretos en todo el repositorio
	@echo "TODO: Implementar Gitleaks (sobre src/ e infra/)"

ci-local: ## Ejecuta el pipeline de CI completo localmente
	@echo "TODO: Esto debe llamar a un script 'scripts/ci-local.sh'"
	@echo "TODO: El script 'ci-local.sh' debe validar la rama y luego ejecutar make lint, test, sast, etc."