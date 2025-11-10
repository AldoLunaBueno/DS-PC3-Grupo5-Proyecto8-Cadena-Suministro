import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Lee archivo requirements y obtiene dependencias con nombre y versión
def parsear_requirements(ruta_requirements):
    dependencias = []
    archivo_req = Path(ruta_requirements)    
    if not archivo_req.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_requirements}")    
    with open(archivo_req, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith('#'):
                if '==' in linea:
                    nombre, version = linea.split('==', 1)
                    dependencias.append({
                        "name": nombre.strip(),
                        "version": version.strip()
                    })    
    return dependencias

# Genera un hash único para cada componente
def generar_hash_componente(nombre, version):
    cadena_componente = f"{nombre}:{version}"
    return hashlib.sha256(cadena_componente.encode()).hexdigest()[:16]

# Genera SBOM estructurado desde requirements
def generar_sbom(ruta_requirements, ruta_salida):    
    dependencias = parsear_requirements(ruta_requirements)    
    componentes = []
    for dep in dependencias:
        componente = {
            "name": dep["name"],
            "version": dep["version"],
            "type": "library",
            "hash": generar_hash_componente(dep["name"], dep["version"])
        }
        componentes.append(componente)    
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0"
            }
        },
        "components": componentes
    }    
    archivo_salida = Path(ruta_salida)
    archivo_salida.parent.mkdir(parents=True, exist_ok=True)    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(sbom, f, indent=2, ensure_ascii=False)    
    return sbom


if __name__ == "__main__":

    import sys
    if len(sys.argv) > 1:
        archivo_requirements = sys.argv[1]
    else:
        archivo_requirements = "requirements.txt"    
    if len(sys.argv) > 2:
        archivo_salida = sys.argv[2]
    else:
        archivo_salida = "sbom.json"  
    try:
        sbom = generar_sbom(archivo_requirements, archivo_salida)
        print(f"SBOM generado en: {archivo_salida}")
        print(f"Total de componentes: {len(sbom['components'])}")
    except Exception as e:
        print(f"Error generando SBOM: {e}", file=sys.stderr)
        sys.exit(1)