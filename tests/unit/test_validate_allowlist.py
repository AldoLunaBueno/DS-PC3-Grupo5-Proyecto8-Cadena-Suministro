import pytest

from supply.validate_allowlist import cargar_json, generar_hash, validar_allowlist


# Pruebas para cargar_json
def test_cargar_json_valido(temp_json_file):
    datos = '{"number": 123, "list": [1, 2, 3]}'
    archivo = temp_json_file(datos)
    resultado = cargar_json(archivo)

    assert resultado == datos


def test_cargar_json_archivo_no_existe():
    with pytest.raises(SystemExit) as exc_info:
        cargar_json("/ruta/inexistente/archivo.json")
    assert exc_info.value.code == 1


def test_cargar_json_invalido(tmp_path):
    invalid_path = tmp_path / "invalid.json"
    with open(invalid_path, "w") as f:
        f.write("invalid json")

    with pytest.raises(SystemExit) as exc_info:
        cargar_json(str(invalid_path))
    assert exc_info.value.code == 1


# Pruebas de generacion de Hash
def test_generar_hash_determinista():
    data = {"name": "numpy", "version": "1.21.0"}
    hash1 = generar_hash(data)
    hash2 = generar_hash(data)

    assert hash1 == hash2


def test_generar_hash_formato():
    data = {"name": "numpy", "version": "1.21.0"}
    hash = generar_hash(data)

    assert len(hash) == 32
    assert all(c in "0123456789abcdef" for c in hash)


def test_generar_hash_contenido_diferente():
    data1 = {"name": "numpy", "version": "1.21.0"}
    data2 = {"name": "numpy", "version": "1.22.0"}

    assert generar_hash(data1) != generar_hash(data2)


# Pruebas de validacion de allowlist
def test_validar_allowlist_exitoso(temp_json_file, sbom_valido, allowlist_valido):
    archivo_sbom = temp_json_file(sbom_valido)
    archivo_allowlist = temp_json_file(allowlist_valido)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is True
    assert "Validación exitosa" in mensaje
    assert "Total de dependencias validadas: 2" in mensaje
    assert "Firma SHA256 del SBOM:" in mensaje
    assert (
        "Todas las dependencias están en el allowlist con versiones correctas"
        in mensaje
    )


def test_validar_allowlist_dependencia_faltante(
    temp_json_file, sbom_valido, allowlist_parcial
):
    archivo_sbom = temp_json_file(sbom_valido)
    archivo_allowlist = temp_json_file(allowlist_parcial)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "Validación fallida" in mensaje
    assert "Dependencia 'fastapi' versión '0.1.0' NO está en el allowlist" in mensaje


def test_validar_allowlist_version_incorrecta(
    temp_json_file, sbom_valido, allowlist_version_incorrecta
):
    archivo_sbom = temp_json_file(sbom_valido)
    archivo_allowlist = temp_json_file(allowlist_version_incorrecta)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "Validación fallida" in mensaje
    assert (
        "versión en SBOM '0.1.0' no coincide con versión en allowlist '0.2.0'"
        in mensaje
    )


def test_validar_allowlist_sbom_sin_components(
    temp_json_file, sbom_sin_componentes, allowlist_valido
):
    archivo_sbom = temp_json_file(sbom_sin_componentes)
    archivo_allowlist = temp_json_file(allowlist_valido)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "El SBOM no contiene la clave 'components'" in mensaje


def test_validar_allowlist_components_no_es_lista(
    temp_json_file, sbom_components_no_array, allowlist_valido
):
    archivo_sbom = temp_json_file(sbom_components_no_array)
    archivo_allowlist = temp_json_file(allowlist_valido)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "El campo 'components' debe ser una lista" in mensaje


def test_validar_allowlist_componente_sin_nombre_o_version(
    temp_json_file, sbom_componentes_incompletos, allowlist_valido
):
    archivo_sbom = temp_json_file(sbom_componentes_incompletos)
    archivo_allowlist = temp_json_file(allowlist_valido)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "Validación fallida" in mensaje
    assert "Componente inválido: falta 'name' o 'version'" in mensaje


def test_validar_allowlist_sbom_vacio(
    temp_json_file, sbom_sin_contenido_componentes, allowlist_valido
):
    archivo_sbom = temp_json_file(sbom_sin_contenido_componentes)
    archivo_allowlist = temp_json_file(allowlist_valido)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is True
    assert "Total de dependencias validadas: 0" in mensaje


def test_validar_allowlist_allowlist_vacio(
    temp_json_file, sbom_valido, allowlist_vacio
):
    archivo_sbom = temp_json_file(sbom_valido)
    archivo_allowlist = temp_json_file(allowlist_vacio)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "Validación fallida" in mensaje


def test_validar_allowlist_componente_sin_version(
    temp_json_file, sbom_componente_sin_version, allowlist_valido
):
    archivo_sbom = temp_json_file(sbom_componente_sin_version)
    archivo_allowlist = temp_json_file(allowlist_valido)

    resultado, mensaje = validar_allowlist(archivo_sbom, archivo_allowlist)

    assert resultado is False
    assert "Validación fallida" in mensaje
    assert "Componente inválido: falta 'name' o 'version'" in mensaje
