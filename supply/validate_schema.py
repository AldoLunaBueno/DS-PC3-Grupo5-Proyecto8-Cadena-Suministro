import json
from pathlib import Path

CAMPOS_REQUERIDOS_RAIZ = ["bomFormat", "specVersion", "version", "metadata", "components"]
CAMPOS_REQUERIDOS_METADATA = ["timestamp", "component"]
CAMPOS_REQUERIDOS_COMPONENTE = ["name", "version", "type"]
CAMPOS_REQUERIDOS_METADATA_COMPONENT = ["type", "name", "version"]

# Verifica que todos los campos requeridos esten presentes
def validar_presencia_campos(datos, campos_requeridos, contexto):    
    errores = []
    for campo in campos_requeridos:
        if campo not in datos:
            errores.append(f"{contexto}: campo requerido '{campo}' no encontrado")
    return errores

# Verifica que un componente cumpla con el esquema
def validar_componente(componente, indice):
    errores = []    
    errores_campo = validar_presencia_campos(
        componente, 
        CAMPOS_REQUERIDOS_COMPONENTE, 
        f"Component[{indice}]"
    )
    errores.extend(errores_campo)    
    if "name" in componente and not isinstance(componente["name"], str):
        errores.append(f"Component[{indice}]: 'name' debe ser string")    
    if "name" in componente and not componente["name"].strip():
        errores.append(f"Component[{indice}]: 'name' no puede estar vacio")    
    if "version" in componente and not isinstance(componente["version"], str):
        errores.append(f"Component[{indice}]: 'version' debe ser string")    
    if "version" in componente and not componente["version"].strip():
        errores.append(f"Component[{indice}]: 'version' no puede estar vacio")    
    if "type" in componente and not isinstance(componente["type"], str):
        errores.append(f"Component[{indice}]: 'type' debe ser string")    
    return errores

# Verifica que metadatos cumplan con el esquema
def validar_metadata(metadata):
    errores = validar_presencia_campos(metadata, CAMPOS_REQUERIDOS_METADATA, "Metadata")    
    if "timestamp" in metadata and not isinstance(metadata["timestamp"], str):
        errores.append("Metadata: 'timestamp' debe ser string")    
    if "component" in metadata:
        errores_componente = validar_presencia_campos(
            metadata["component"],
            CAMPOS_REQUERIDOS_METADATA_COMPONENT,
            "Metadata.component"
        )
        errores.extend(errores_componente)    
    return errores

# Valida que el SBOM cumpla con el esquema
def validar_esquema_sbom(ruta_sbom):
    errores = []    
    archivo_sbom = Path(ruta_sbom)
    if not archivo_sbom.exists():
        return False, [f"Archivo no encontrado: {ruta_sbom}"]    
    try:
        with open(archivo_sbom, 'r', encoding='utf-8') as f:
            sbom = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Error parseando JSON: {e}"]    
    if not isinstance(sbom, dict):
        return False, ["El SBOM debe ser un objeto JSON"]    
    errores_raiz = validar_presencia_campos(sbom, CAMPOS_REQUERIDOS_RAIZ, "Root")
    errores.extend(errores_raiz)    
    if "metadata" in sbom:
        errores_metadata = validar_metadata(sbom["metadata"])
        errores.extend(errores_metadata)    
    if "components" in sbom:
        if not isinstance(sbom["components"], list):
            errores.append("'components' debe ser un array")
        else:
            for idx, componente in enumerate(sbom["components"]):
                if not isinstance(componente, dict):
                    errores.append(f"Component[{idx}]: debe ser un objeto")
                    continue
                errores_componente = validar_componente(componente, idx)
                errores.extend(errores_componente)    
    es_valido = len(errores) == 0
    return es_valido, errores


if __name__ == "__main__":

    import sys    
    if len(sys.argv) > 1:
        archivo_sbom = sys.argv[1]
    else:
        archivo_sbom = "sbom.json"   
    es_valido, errores = validar_esquema_sbom(archivo_sbom)    
    if es_valido:
        print(f"SBOM válido: {archivo_sbom}")
        sys.exit(0)
    else:
        print(f"SBOM inválido")
        print("\nErrores encontrados:")
        for error in errores:
            print(f"  - {error}")
        sys.exit(1)