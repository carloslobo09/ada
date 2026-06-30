from fastapi.testclient import TestClient

EXTRACTION_FIELDS = [
    {"name": "numero_dni", "label": "Numero de DNI"},
    {"name": "nombre_completo", "label": "Nombre completo"},
]

NEW_CONFIG = [
    {
        "field": "numero_dni",
        "normalization": ["digits_only"],
        "comparison": "equals",
        "critical": True,
        "required_expected": True,
    },
    {
        "field": "nombre_completo",
        "normalization": ["trim", "uppercase", "remove_accents", "collapse_spaces"],
        "comparison": "fuzzy_70",
        "critical": True,
        "required_expected": False,
    },
]


def _payload(tipo_id: str, prompt_text: str = "Prompt v2") -> dict:
    return {
        "tipo_documento_id": tipo_id,
        "prompt_text": prompt_text,
        "extraction_fields": EXTRACTION_FIELDS,
        "cross_validation_config": NEW_CONFIG,
    }


def test_seed_inserta_version_publicada(client: TestClient, seeded_tipo_id: str) -> None:
    response = client.get("/prompt-versions")
    assert response.status_code == 200
    versions = response.json()
    assert len(versions) == 1
    assert versions[0]["estado"] == "publicada"
    assert versions[0]["numero"] == 1
    assert versions[0]["tipo_documento_id"] == seeded_tipo_id


def test_seed_trae_extraction_fields(client: TestClient) -> None:
    versions = client.get("/prompt-versions").json()
    detail = client.get(f"/prompt-versions/{versions[0]['id']}").json()
    nombres = {f["name"] for f in detail["extraction_fields"]}
    assert "numero_dni" in nombres
    assert "nombre_completo" in nombres


def test_create_version_arranca_en_borrador(
    client: TestClient, seeded_tipo_id: str
) -> None:
    response = client.post("/prompt-versions", json=_payload(seeded_tipo_id))
    assert response.status_code == 201
    created = response.json()
    assert created["estado"] == "borrador"
    assert created["numero"] == 2
    assert len(created["extraction_fields"]) == 2


def test_create_sin_extraction_fields_devuelve_422(
    client: TestClient, seeded_tipo_id: str
) -> None:
    payload = _payload(seeded_tipo_id)
    payload["extraction_fields"] = []
    response = client.post("/prompt-versions", json=payload)
    assert response.status_code == 422


def test_publish_archiva_la_publicada_anterior(
    client: TestClient, seeded_tipo_id: str
) -> None:
    created = client.post("/prompt-versions", json=_payload(seeded_tipo_id)).json()

    published = client.patch(f"/prompt-versions/{created['id']}/publish").json()
    assert published["estado"] == "publicada"

    versions = client.get("/prompt-versions").json()
    publicadas = [v for v in versions if v["estado"] == "publicada"]
    assert len(publicadas) == 1
    assert publicadas[0]["id"] == created["id"]

    archivadas = [v for v in versions if v["estado"] == "archivada"]
    assert len(archivadas) == 1


def test_delete_version_publicada_devuelve_409(client: TestClient) -> None:
    versions = client.get("/prompt-versions").json()
    publicada_id = next(v["id"] for v in versions if v["estado"] == "publicada")

    response = client.delete(f"/prompt-versions/{publicada_id}")
    assert response.status_code == 409


def test_delete_version_borrador_funciona(
    client: TestClient, seeded_tipo_id: str
) -> None:
    created = client.post("/prompt-versions", json=_payload(seeded_tipo_id)).json()
    response = client.delete(f"/prompt-versions/{created['id']}")
    assert response.status_code == 204
    listed = client.get("/prompt-versions").json()
    assert created["id"] not in [v["id"] for v in listed]


def test_get_version_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.get("/prompt-versions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_filtrar_versiones_por_tipo(client: TestClient, seeded_tipo_id: str) -> None:
    response = client.get(f"/prompt-versions?tipo_documento_id={seeded_tipo_id}")
    assert response.status_code == 200
    versions = response.json()
    assert all(v["tipo_documento_id"] == seeded_tipo_id for v in versions)
