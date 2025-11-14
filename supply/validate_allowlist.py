import hashlib
import json
import sys
from pathlib import Path


def cargar_json(ruta_json):
    path = Path(ruta_json)

    if not path.exists():
        print(f"Archivo no encontrado en {ruta_json}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON malformado en {ruta_json}. Detalles: {e}")
        sys.exit(1)


def generar_hash(json_contenido):
    json_contenido = json.dumps(json_contenido, sort_keys=True)
    return hashlib.sha256(json_contenido.encode()).hexdigest()[:32]


def validar_allowlist(ruta_sbom, ruta_allowlist):
    sbom = cargar_json(ruta_sbom)
    sbom_hash = generar_hash(sbom)
    allowlist = cargar_json(ruta_allowlist)

    if "components" not in sbom:
        return False, "El SBOM no contiene la clave 'components'."

    components = sbom.get("components", [])
    if not isinstance(components, list):
        return False, "El campo 'components' debe ser una lista."

    errors = []

    for component in components:
        name = component.get("name")
        version = component.get("version")

        if not name or not version:
            errors.append("Componente inválido: falta 'name' o 'version'.")
            continue

        if name not in allowlist:
            errors.append(
                (f"Dependencia '{name}' versión '{version}' NO está en el allowlist.")
            )
            continue

        allowed_version = allowlist[name]
        if version != allowed_version:
            errors.append(
                (
                    f"Dependencia '{name}': versión en SBOM '{version}' "
                    f"no coincide con versión en allowlist "
                    f"'{allowed_version}'."
                )
            )

    if errors:
        mensaje = "Validación fallida:\n" + "\n".join(errors)
        return False, mensaje

    mensaje = (
        f"Validación exitosa\n"
        f"Total de dependencias validadas: {len(components)}\n"
        f"Firma SHA256 del SBOM: {sbom_hash}\n"
        f"Todas las dependencias están en el allowlist con versiones correctas."
    )

    return True, mensaje


if __name__ == "__main__":
    if len(sys.argv) > 1:
        archivo_allowlist = sys.argv[1]
    else:
        archivo_allowlist = "allowlist.json"
    if len(sys.argv) > 2:
        archivo_sbom = sys.argv[2]
    else:
        archivo_sbom = "sbom.json"

    es_valido, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    if es_valido:
        print(mensaje)
        sys.exit(0)
    else:
        print(mensaje)
        sys.exit(1)
