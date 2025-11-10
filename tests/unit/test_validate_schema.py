import pytest
from unittest.mock import patch, mock_open
from supply.validate_schema import (
    validar_presencia_campos,
    validar_componente,
    validar_metadata,
    validar_esquema_sbom
)

# validar presencia de campos
@pytest.mark.parametrize("datos,campos,contexto,errores_esperados", [
    ({"name": "test", "version": "1.0"}, ["name", "version"], "Test", []),
    ({"name": "test"}, ["name", "version"], "Test", ["Test: campo requerido 'version' no encontrado"]),
    ({}, ["name", "version"], "Test", ["Test: campo requerido 'name' no encontrado", "Test: campo requerido 'version' no encontrado"]),
])
def test_validar_presencia_campos_parametrizado(datos, campos, contexto, errores_esperados):
    errores = validar_presencia_campos(datos, campos, contexto)
    assert errores == errores_esperados

# validar componente
def test_validar_componente_valido():
    componente = {"name": "pytest", "version": "8.2.2", "type": "library"}
    errores = validar_componente(componente, 0)
    assert errores == []

# validad campos faltantes
@pytest.mark.parametrize("componente,error_substring", [
    ({"version": "1.0", "type": "lib"}, "campo requerido 'name' no encontrado"),
    ({"name": "pkg", "type": "lib"}, "campo requerido 'version' no encontrado"),
    ({"name": "pkg", "version": "1.0"}, "campo requerido 'type' no encontrado"),
])
def test_validar_componente_campos_faltantes_parametrizado(componente, error_substring):
    errores = validar_componente(componente, 0)
    assert any(error_substring in error for error in errores)

# valores vacios
@pytest.mark.parametrize("componente,error_substring", [
    ({"name": "", "version": "1.0", "type": "lib"}, "'name' no puede estar vacio"),
    ({"name": "pkg", "version": "", "type": "lib"}, "'version' no puede estar vacio"),
])
def test_validar_componente_valores_vacios_parametrizado(componente, error_substring):
    errores = validar_componente(componente, 0)
    assert any(error_substring in error for error in errores)

# validar metadata
def test_validar_metadata_valida():
    metadata = {
        "timestamp": "2025-11-03T10:00:00+00:00",
        "component": {"type": "application", "name": "test", "version": "1.0"}
    }
    errores = validar_metadata(metadata)
    assert errores == []

# campos faltantes
@pytest.mark.parametrize("metadata,error_substring", [
    ({"component": {"type": "app", "name": "test", "version": "1.0"}}, "'timestamp' no encontrado"),
    ({"timestamp": "2025-11-03"}, "'component' no encontrado"),
])
def test_validar_metadata_campos_faltantes_parametrizado(metadata, error_substring):
    errores = validar_metadata(metadata)
    assert any(error_substring in error for error in errores)

# validar esquema sbom
def test_validar_esquema_sbom_valido(temp_sbom_file, sbom_valido):
    sbom_file = temp_sbom_file(sbom_valido)
    es_valido, errores = validar_esquema_sbom(sbom_file)
    assert es_valido is True
    assert errores == []

def test_validar_esquema_sbom_archivo_no_existe():
    es_valido, errores = validar_esquema_sbom("/ruta/inexistente.json")
    assert es_valido is False
    assert "Archivo no encontrado" in errores[0]

def test_validar_esquema_sbom_json_malformado(temp_sbom_file, sbom_json_malformado):
    sbom_file = temp_sbom_file(sbom_json_malformado)
    es_valido, errores = validar_esquema_sbom(sbom_file)
    assert es_valido is False
    assert "Error parseando JSON" in errores[0]

# caso limite
@pytest.mark.parametrize("fixture_name,error_substring", [
    ("sbom_sin_bomformat", "'bomFormat' no encontrado"),
    ("sbom_sin_metadata", "'metadata' no encontrado"),
    ("sbom_componente_sin_version", "'version' no encontrado"),
    ("sbom_componente_version_vacia", "'version' no puede estar vacio"),
])
def test_validar_esquema_sbom_casos_limite_parametrizado(temp_sbom_file, request, fixture_name, error_substring):
    sbom_data = request.getfixturevalue(fixture_name)
    sbom_file = temp_sbom_file(sbom_data)
    es_valido, errores = validar_esquema_sbom(sbom_file)
    assert es_valido is False
    assert any(error_substring in error for error in errores)

# componentes no son arrays
def test_validar_esquema_sbom_components_no_array(temp_sbom_file, sbom_components_no_array):
    sbom_file = temp_sbom_file(sbom_components_no_array)
    es_valido, errores = validar_esquema_sbom(sbom_file)
    assert es_valido is False
    assert any("'components' debe ser un array" in error for error in errores)

# mock de File I/O con autospec=True
@patch('builtins.open', new_callable=mock_open, read_data='{"bomFormat": "CycloneDX", "specVersion": "1.4", "version": 1, "metadata": {"timestamp": "2025-11-03", "component": {"type": "application", "name": "test", "version": "1.0"}}, "components": []}')
@patch('supply.validate_schema.Path.exists', autospec=True)
def test_validar_esquema_sbom_mock_autospec(mock_exists, mock_file):
    mock_exists.return_value = True
    es_valido, errores = validar_esquema_sbom("mocked.json")
    assert es_valido is True
    assert errores == []
    mock_file.assert_called_once()