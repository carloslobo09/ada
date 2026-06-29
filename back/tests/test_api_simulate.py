import io
import json

from fastapi.testclient import TestClient


def _active_version_id(client: TestClient) -> str:
    versions = client.get("/prompt-versions").json()
    return next(v["id"] for v in versions if v["estado"] == "publicada")


def test_simulate_devuelve_aprobado_con_mock(client: TestClient) -> None:
    version_id = _active_version_id(client)
    response = client.post(
        f"/prompt-versions/{version_id}/simulate",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision_status"] == "approved"
    assert body["normalized_extraction"]["numero_dni"] == "40123456"
    assert body["prompt_version_id"] == version_id


def test_simulate_no_persiste_el_caso(client: TestClient) -> None:
    version_id = _active_version_id(client)
    before = client.get("/cases").json()
    client.post(
        f"/prompt-versions/{version_id}/simulate",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
    )
    after = client.get("/cases").json()
    assert len(after["items"]) == len(before["items"])


def test_simulate_con_expected_completo(client: TestClient) -> None:
    version_id = _active_version_id(client)
    expected = {"numero_dni": "40123456", "nombre_completo": "Lobo Carlos Ignacio"}
    response = client.post(
        f"/prompt-versions/{version_id}/simulate",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"expected": json.dumps(expected)},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision_status"] == "approved"
    assert len(body["cross_validation_results"]) == 2


def test_simulate_falta_required_rechaza(client: TestClient) -> None:
    version_id = _active_version_id(client)
    response = client.post(
        f"/prompt-versions/{version_id}/simulate",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"expected": json.dumps({"nombre_completo": "Carlos"})},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision_status"] == "rejected"
    assert "numero_dni" in body["decision_reason"]
    assert body["raw_extraction"] is None


def test_simulate_version_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.post(
        "/prompt-versions/00000000-0000-0000-0000-000000000000/simulate",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
    )
    assert response.status_code == 404


def test_simulate_mime_invalido_devuelve_415(client: TestClient) -> None:
    version_id = _active_version_id(client)
    response = client.post(
        f"/prompt-versions/{version_id}/simulate",
        files={"file": ("a.txt", io.BytesIO(b"x"), "text/plain")},
    )
    assert response.status_code == 415
