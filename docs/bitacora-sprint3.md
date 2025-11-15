# Bitácora Sprint 3: Automatización de Seguimiento de Hallazgos de Seguridad

## Descripción General

En este sprint se implementó un mecanismo automático para actualizar el campo personalizado "trend" en los issues del proyecto de GitHub. Este sistema cierra el ciclo de DevSecOps conectando el análisis de hallazgos de seguridad con la gestión de proyectos, permitiendo visualizar si la calidad de seguridad mejora o empeora con cada cambio.

## 1. Problema Identificado

El pipeline de CI genera reportes de seguridad (SBOM, dashboard con hallazgos) en cada PR, pero **no había forma automática de comunicar al tablero del proyecto** si la cantidad de hallazgos aumentó o disminuyó. Esto requería actualización manual del campo "trend" en cada issue, introduciendo:

- Carga manual repetitiva
- Riesgo de inconsistencia
- Falta de automatización en el ciclo DevSecOps

## 2. Solución Implementada: Job `actualizar-trend`

Se agregó un nuevo job al workflow de CI (`.github/workflows/ci.yml`) que se ejecuta **después** de que el job `gates` complete exitosamente.

### Componentes

#### 2.1 Ubicación
Job integrado en `.github/workflows/ci.yml` bajo la etiqueta `actualizar-trend`.

#### 2.2 Condición de Ejecución
```yaml
if: github.event_name == 'pull_request'
needs: gates
```

Se ejecuta solo en contexto de pull requests y depende del éxito del job anterior `gates`.

#### 2.3 Pasos del Job

**Paso 1: Descargar repositorio**
- Realiza un checkout del código para acceder al contexto de ejecución.

**Paso 2: Autenticar GitHub CLI**
- Usa el secret `GH_TOKEN` para autenticar comandos de `gh` que interactúan con la API de GitHub.

**Paso 3: Descargar artefactos**
- Descarga el artefacto `security-reports` generado por el job `gates`, que contiene:
  - `sbom.json`: Software Bill of Materials
  - `dashboard.html`: Dashboard con métricas de seguridad incluyendo hallazgos

**Paso 4: Obtener issue y actualizar trend**
- **Extrae el issue vinculado:** Intenta obtener el número del issue mediante la API de GitHub (referencias de cierre) o búsqueda en el body del PR con patrones "Closes #N", "Fixes #N", "Resolves #N".
- **Cuenta hallazgos actuales:** Extrae el número de hallazgos del `dashboard.html` mediante regex.
- **Recupera hallazgos previos:** Busca en el body del issue un patrón como "Hallazgos previos: N" o "Hallazgos anteriores: N".
- **Determina tendencia:**
  - Si `hallazgos_actuales < hallazgos_previos`: trend = "mejora"
  - Si `hallazgos_actuales > hallazgos_previos`: trend = "empeora"
  - Si son iguales: no actualiza (evita ruido)
- **Actualiza el proyecto:** Usa `gh project item-edit` para actualizar el custom field "trend" del issue en el proyecto número 11.

## 3. Flujo de Ejecución

```
PR Merged
    |
    v
Job: gates (CI completo: tests, SBOM, validaciones)
    |
    ├─→ Genera: sbom.json, dashboard.html
    |
    v
Job: actualizar-trend (con needs: gates)
    |
    ├─→ Descarga artefactos
    ├─→ Extrae issue vinculado
    ├─→ Cuenta hallazgos actuales
    ├─→ Recupera hallazgos previos
    ├─→ Compara y determina trend
    └─→ Actualiza field "trend" en el tablero
```

## 4. Refactorización y Decisiones de Diseño

### 4.1 Consolidación en un Solo Workflow

Inicialmente se creó un workflow separado (`update-trend-field.yml`) que se disparaba en eventos de PR cerrado. Sin embargo, presentaba problemas:

- **Race condition:** Los artefactos se generan durante CI, pero el workflow separado intenta descargarlos en otro contexto.
- **Complejidad:** Dos workflows independientes para una sola función.
- **Duplicación:** Lógica compartida entre ambos workflows.

**Decisión:** Integrar el job como parte del workflow de CI, ejecutándose secuencialmente después del job `gates`.

**Beneficios:**
- Acceso garantizado a los artefactos sin race conditions.
- Ejecución predecible y secuencial.
- Un solo archivo de configuración para toda la lógica de CI y análisis.
- Mantiene el principio DRY (Don't Repeat Yourself).

### 4.2 Tolerancia a Fallos

El job está diseñado con tolerancia a fallos:

```bash
[ -z "$ISSUE" ] && exit 0
[ -z "$HALLAZGOS" ] && exit 0
```

Si no se encuentra issue vinculado o si no se pueden extraer hallazgos, el job termina exitosamente sin fallar el workflow. Esto evita bloquear PRs por problemas en la automatización secundaria.

## 5. Ventajas de la Implementación

- **Automatización:** Elimina actualización manual del campo trend.
- **Visibilidad:** El tablero del proyecto refleja automáticamente cambios en hallazgos.
- **Trazabilidad:** Cada issue tiene un registro claro de si la seguridad mejoró o empeoró.
- **Integración:** Cierra completamente el ciclo DevSecOps: análisis automático -> actualización automática del tracking.
- **Mantenibilidad:** Centraliza la lógica en un solo workflow según principios de DRY.

## 6. Configuración Requerida

Para que el job funcione correctamente, se necesita:

1. **Secret `GH_TOKEN`:** Token de GitHub con permisos `repo`, `read:org`, `project` para actualizar campos de proyecto.
2. **Proyecto número 11:** El tablero debe existir con un custom field llamado "trend" que tenga opciones "mejora" y "empeora".
3. **Issues vinculados:** Los PRs deben incluir referencias de cierre válidas (Closes #N, etc.).
4. **Formato en body del issue:** Para hallazgos previos, incluir línea como "Hallazgos previos: N" o "Hallazgos anteriores: N".

## 7. Próximos Pasos Potenciales

- Extender el tracking a otros custom fields (ej: "complejidad", "prioridad").
- Agregar notificaciones o comentarios automáticos en issues.
- Integrar métricas de tendencia a lo largo del tiempo.
- Implementar umbrales de alerta si los hallazgos superan cierto límite.
