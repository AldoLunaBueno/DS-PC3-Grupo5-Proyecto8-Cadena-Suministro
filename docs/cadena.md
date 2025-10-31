# Esquema SBOM - cadena de suministro

## Formato

El SBOM sigue el formato **CycloneDX 1.4** y se serializa en JSON.

## Estructura del Esquema

### 1. Campos Raiz (Root)

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `bomFormat` | string | Sí | Formato del BOM. Valor: "CycloneDX" |
| `specVersion` | string | Sí | Version de la especificacion. Valor: "1.4" |
| `version` | integer | Sí | Version del documento SBOM. Valor: 1 |
| `metadata` | object | Sí | Metadatos del SBOM |
| `components` | array | Sí | Lista de componentes/dependencias |

### 2. Estructura de `metadata`

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `timestamp` | string | Sí | Fecha y hora de generacion en formato ISO 8601 (UTC) |
| `component` | object | Sí | Informacion del componente principal (aplicacion) |

#### 2.1. Estructura de `metadata.component`

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `type` | string | Sí | Tipo de componente. Valor: "application" |
| `name` | string | Sí | Nombre de la aplicacion. Valor: "cadena-suministro" |
| `version` | string | Sí | Version de la aplicacion. Valor: "1.0.0" |

### 3. Estructura de `components` (Array de objetos)

Cada elemento del array `components` representa una dependencia y debe contener:

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `name` | string | Sí | Nombre del paquete/libreria (no vacio) |
| `version` | string | Sí | Version del paquete (no vacio) |
| `type` | string | Sí | Tipo de componente. Valor: "library" |
| `hash` | string | No | Hash SHA256 truncado (16 caracteres) del componente |