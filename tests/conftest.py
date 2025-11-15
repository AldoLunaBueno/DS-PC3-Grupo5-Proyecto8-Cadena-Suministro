import json
import os
import tempfile

import pytest

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
                "version": "1.0.0",
            },
        },
        "components": [
            {
                "name": "pytest",
                "version": "8.2.2",
                "type": "library",
                "hash": "a1b2c3d4e5f67890",
            },
            {
                "name": "fastapi",
                "version": "0.1.0",
                "type": "library",
                "hash": "1234567890abcdef",
            },
        ],
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
                "version": "1.0.0",
            },
        },
        "components": [],
    }


# SBOM sin el campo componentes
@pytest.fixture
def sbom_sin_componentes():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0",
            },
        },
    }


# SBOM sin el contenido de los componentes
@pytest.fixture
def sbom_sin_contenido_componentes():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0",
            },
        },
        "components": [],
    }


# SBOM sin campo metadata
@pytest.fixture
def sbom_sin_metadata():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "components": [],
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
                "version": "1.0.0",
            },
        },
        "components": [{"name": "pytest", "type": "library"}],
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
                "version": "1.0.0",
            },
        },
        "components": [{"name": "pytest", "version": "", "type": "library"}],
    }


# SBOM con componentes incompletos
@pytest.fixture
def sbom_componentes_incompletos():
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": "2025-11-03T10:00:00+00:00",
            "component": {
                "type": "application",
                "name": "cadena-suministro",
                "version": "1.0.0",
            },
        },
        "components": [
            {"name": "fastapi", "version": "0.118.0", "type": "library"},
            {"name": "flake8"},
            {"version": "7.1.0"},
            {"name": "numpy", "version": "1.21.0", "type": "library"},
        ],
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
                "version": "1.0.0",
            },
        },
        "components": "not-an-array",
    }


# JSON mal generado
@pytest.fixture
def sbom_json_malformado():
    return "{invalid json: roto"


# FIXTURES: Allowlists de ejemplo


@pytest.fixture
def allowlist_valido():
    return {"pytest": "8.2.2", "fastapi": "0.1.0"}


@pytest.fixture
def allowlist_parcial():
    return {"pytest": "8.2.2"}


@pytest.fixture
def allowlist_version_incorrecta():
    return {"pytest": "8.2.2", "fastapi": "0.2.0"}


@pytest.fixture
def allowlist_vacio():
    return {}


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


@pytest.fixture
def temp_json_file():
    temp_files = []

    def _create_temp_file(data):
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, temp_file)
        temp_file.flush()
        temp_files.append(temp_file.name)
        return temp_file.name

    yield _create_temp_file

    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
