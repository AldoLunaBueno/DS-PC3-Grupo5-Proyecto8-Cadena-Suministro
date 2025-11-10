import pytest
import json

# FIXTURES: SBOMs de ejemplo 

@pytest.fixture
def sbom_valido():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0"
            }
        },
        "components": [
            {
                "name": "pytest",
                "version": "8.2.2",
                "type": "library",
                "hash": "a1b2c3d4e5f67890"
            },
            {
                "name": "fastapi",
                "version": "0.1.0",
                "type": "library",
                "hash": "1234567890abcdef"
            }
        ]
    }

# SBOM sin el campo bomFormat
@pytest.fixture
def sbom_sin_bomformat():
    return {
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0"
            }
        },
        "components": []
    }

# SBOM sin campo metadata
@pytest.fixture
def sbom_sin_metadata():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "components": []
    }

# SBOM com componentes pero sin version
@pytest.fixture
def sbom_componente_sin_version():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0"
            }
        },
        "components": [
            {
                "name": "pytest",
                "type": "library"
            }
        ]
    }

# SBOM con version vacia
@pytest.fixture
def sbom_componente_version_vacia():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0"
            }
        },
        "components": [
            {
                "name": "pytest",
                "version": "",
                "type": "library"
            }
        ]
    }

# SBOM componentes que no son array
@pytest.fixture
def sbom_components_no_array():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0"
            }
        },
        "components": "not-an-array"
    }

# JSON mal generado
@pytest.fixture
def sbom_json_malformado():
    return "{invalid json: roto"


# FIXTURES: ejemplo de requirements.txt

@pytest.fixture
def requirements_valido():
    return """# Comentario
pytest==8.2.2
fastapi==0.118.0
black==25.9.0

# Otro comentario
flake8==7.1.0"""


# FIXTURES: Paths temporales

@pytest.fixture
def temp_sbom_file(tmp_path):
    def _create_sbom(content):
        sbom_file = tmp_path / "test_sbom.json"
        if isinstance(content, dict):
            sbom_file.write_text(json.dumps(content, indent=2))
        else:
            sbom_file.write_text(content)
        return str(sbom_file)
    return _create_sbom

# requirements.txt temporal
@pytest.fixture
def temp_requirements_file(tmp_path):
    def _create_requirements(content):
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(content)
        return str(req_file)
    return _create_requirements