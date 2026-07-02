import io
import json

from fastapi.testclient import TestClient


def _post_case(
    client: TestClient,
    tipo_id: str,
    *,
    expected: dict | None = None,
):
    data: dict = {"tipo_documento_id": tipo_id}
    if expected is not None:
        data["expected"] = json.dumps(expected)
    return client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data=data,
    )


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_case_solo_extraccion(client: TestClient, seeded_tipo_id: str) -> None:
    response = _post_case(client, seeded_tipo_id)
    assert response.status_code == 201

    body = response.json()
    assert body["estado"] == "procesado"
    assert body["decision"]["veredicto"] == "approved"
    assert body["documento"] is not None
    assert body["documento"]["content_type"] == "image/png"
    assert body["documento"]["hash_integridad"]
    assert body["documento"]["tipo_documento_id"] == seeded_tipo_id

    campos = body["decision"]["refs_evidencias"]["resultado_extraccion"]["campos_normalizados"]
    assert campos["numero_dni"] == "40123456"
    assert campos["nombre_completo"] == "LOBO CARLOS IGNACIO"

    reglas = body["decision"]["refs_evidencias"]["evaluacion_reglas"]
    assert all(r["passed"] for r in reglas)


def test_decision_referencia_la_version_activa(
    client: TestClient, seeded_tipo_id: str
) -> None:
    active = next(
        v for v in client.get("/prompt-versions").json() if v["estado"] == "publicada"
    )
    created = _post_case(client, seeded_tipo_id).json()
    salida = created["decision"]["refs_evidencias"]["salida_modelo"]
    assert salida["ref_version_prompt"] == active["id"]


def test_create_case_con_expected_aprueba(client: TestClient, seeded_tipo_id: str) -> None:
    expected = {
        "numero_dni": "40123456",
        "nombre_completo": "Lobo Carlos Ignacio",
        "fecha_nacimiento": "1997-08-15",
    }
    response = _post_case(client, seeded_tipo_id, expected=expected)
    assert response.status_code == 201
    body = response.json()
    assert body["decision"]["veredicto"] == "approved"
    assert body["decision"]["expected_received"] == expected
    cruzados = body["decision"]["cross_validation_results"]
    assert len(cruzados) == 3
    assert all(r["passed"] for r in cruzados)


def test_create_case_expected_no_coincide_rechaza(
    client: TestClient, seeded_tipo_id: str
) -> None:
    expected = {
        "numero_dni": "99999999",
        "nombre_completo": "Lobo Carlos Ignacio",
        "fecha_nacimiento": "1997-08-15",
    }
    response = _post_case(client, seeded_tipo_id, expected=expected)
    assert response.status_code == 201
    body = response.json()
    assert body["decision"]["veredicto"] == "rejected"
    assert "numero_dni" in body["decision"]["motivos"]


def test_create_case_criticos_incompletos_rechaza_pre_llm(
    client: TestClient, seeded_tipo_id: str
) -> None:
    # Los tres campos criticos del cruce son obligatorios: enviar solo uno
    # rechaza el caso antes de invocar al modelo.
    response = _post_case(client, seeded_tipo_id, expected={"numero_dni": "40123456"})
    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "rechazado_pre_llm"
    assert "nombre_completo" in body["decision"]["motivos"]
    assert "fecha_nacimiento" in body["decision"]["motivos"]


def test_create_case_falta_required_rechaza_pre_llm(
    client: TestClient, seeded_tipo_id: str
) -> None:
    response = _post_case(client, seeded_tipo_id, expected={"nombre_completo": "Carlos"})
    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "rechazado_pre_llm"
    assert body["decision"]["veredicto"] == "rejected"
    assert "numero_dni" in body["decision"]["motivos"]
    assert body["decision"]["refs_evidencias"] is None
    assert body["decision"]["expected_received"] == {"nombre_completo": "Carlos"}


def test_create_case_campo_desconocido_rechaza_pre_llm(
    client: TestClient, seeded_tipo_id: str
) -> None:
    expected = {"numero_dni": "40123456", "campo_inventado": "x"}
    response = _post_case(client, seeded_tipo_id, expected=expected)
    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "rechazado_pre_llm"
    assert body["decision"]["veredicto"] == "rejected"
    assert "campo_inventado" in body["decision"]["motivos"]


def test_create_case_tipo_inexistente_devuelve_503(client: TestClient) -> None:
    response = _post_case(client, "00000000-0000-0000-0000-000000000000")
    assert response.status_code == 503


def test_create_case_mime_invalido_devuelve_415(
    client: TestClient, seeded_tipo_id: str
) -> None:
    response = client.post(
        "/cases",
        files={"file": ("x.txt", io.BytesIO(b"contenido"), "text/plain")},
        data={"tipo_documento_id": seeded_tipo_id},
    )
    assert response.status_code == 415


def test_create_case_expected_json_invalido_400(
    client: TestClient, seeded_tipo_id: str
) -> None:
    response = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id, "expected": "{no es json"},
    )
    assert response.status_code == 400


def test_get_case_not_found(client: TestClient) -> None:
    response = client.get("/cases/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_cases_empty(client: TestClient) -> None:
    response = client.get("/cases")
    assert response.status_code == 200
    assert response.json() == {"items": [], "limit": 50, "offset": 0}


def test_round_trip(client: TestClient, seeded_tipo_id: str) -> None:
    created = _post_case(client, seeded_tipo_id).json()
    fetched = client.get(f"/cases/{created['id']}").json()
    assert fetched["id"] == created["id"]
    assert fetched["decision"]["veredicto"] == "approved"
    assert fetched["documento"]["hash_integridad"] == created["documento"]["hash_integridad"]
