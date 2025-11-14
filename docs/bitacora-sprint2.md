# Bitácora Sprint 2

## Verificación de Firma (Hash) y Allowlist

La política de allowlist es un mecanismo de seguridad que asegura que **todas las dependencias del proyecto han sido revisadas y aprobadas** antes de su inclusión. Esto previene la introducción no autorizada de paquetes maliciosos o no verificados en la cadena de suministro.

### Componentes

#### 1. Archivo `allowlist.json`
 Define la lista de dependencias permitidas con sus versiones aprobadas.

**Estructura:**
```json
{
  "nombre-paquete": "versión",
  "fastapi": "0.118.0",
  "pytest": "8.2.2"
  ...
}
```

#### 2. Script `supply/validate_allowlist.py`

**Ubicación:** `supply/validate_allowlist.py`

Valida que todas las dependencias del SBOM estén en el allowlist con las versiones correctas.

**Funcionalidades:**
1. **Generación de Firma SHA256:** Calcula un hash SHA256 del contenido completo del SBOM para detectar cualquier modificación no autorizada.
2. **Validación de Dependencias:** Verifica que cada paquete en el SBOM exista en el allowlist.
3. **Validación de Versiones:** Asegura que la versión de cada dependencia coincida exactamente con la versión aprobada.

**Uso:**

```bash
# Uso básico (busca sbom.json y allowlist.json en raíz)
python3 supply/validate_allowlist.py

# Especificar rutas personalizadas
python3 supply/validate_allowlist.py ruta/a/sbom.json ruta/a/allowlist.json
```

**Código de Salida:**
- `0`: Validación exitosa (todas las dependencias están permitidas)
- `1`: Validación fallida (dependencia no autorizada o versión no coincide)

**Salida del Script:**

En caso de éxito:
```
Validación exitosa
Total de dependencias validadas: 9
Firma SHA256 del SBOM: abc123...
Todas las dependencias están en el allowlist con versiones correctas.
```

En caso de error:
```
Validación fallida:
Dependencia 'paquete-no-autorizado' versión '1.0.0' NO está en el allowlist.
```

### Flujo de Validación

```
┌─────────────────┐
│   SBOM.json     │
└────────┬────────┘
         │
         ├─→ Generar Hash SHA256
         │
         ├─→ Extraer dependencias
         │
         └─→ Comparar contra allowlist.json
                    │
                    ├─→ ¿Existe en allowlist?
                    │
                    ├─→ ¿Versión coincide?
                    │
                    └─→ Resultado: Aprobado/Rechazado
```

### Ventajas de la Política de Allowlist

- **Seguridad:** Previene la inclusión de paquetes maliciosos
- **Trazabilidad:** Registro claro de qué versiones están aprobadas
- **Control:** Solo dependencias revisadas pueden usarse
- **Auditoría:** Facilita auditorías de seguridad y cumplimiento
- **Reproducibilidad:** Garantiza versiones consistentes en todos los entornos