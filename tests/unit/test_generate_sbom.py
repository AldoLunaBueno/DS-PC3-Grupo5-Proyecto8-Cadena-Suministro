import pytest

from supply.generate_sbom import generar_sbom, parsear_requirements


def test_parsear_requirements_archivo_no_existe():
    with pytest.raises(FileNotFoundError):
        parsear_requirements("/ruta/inexistente.txt")


# Test de generar_sbom
def test_generar_sbom_basico(temp_requirements_file, requirements_valido, tmp_path):
    req_file = temp_requirements_file(requirements_valido)
    output_file = tmp_path / "sbom.json"
    sbom = generar_sbom(req_file, str(output_file))
    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.4"
    assert "metadata" in sbom
    assert "components" in sbom
    assert len(sbom["components"]) == 4
    assert output_file.exists()
