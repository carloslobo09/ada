import io

from fastapi.testclient import TestClient


def _create_case(client: TestClient, tipo_id: str) -> dict:
    response = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": tipo_id},
    )
    assert response.status_code == 201
    return response.json()


def test_caso_nace_en_pendiente(client: TestClient, seeded_tipo_id: str) -> None:
    body = _create_case(client, seeded_tipo_id)
    assert body["estado_recontrol"] == "pendiente"
    assert body["observacion_recontrol"] is None
    assert body["fecha_recontrol"] is None


def test_marcar_correcto(client: TestClient, seeded_tipo_id: str) -> None:
    caso = _create_case(client, seeded_tipo_id)
    response = client.patch(
        f"/cases/{caso['id']}/review",
        json={"estado_recontrol": "correcto", "observacion_recontrol": None},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["estado_recontrol"] == "correcto"
    assert body["fecha_recontrol"] is not None


def test_marcar_incorrecto_con_observacion(client: TestClient, seeded_tipo_id: str) -> None:
    caso = _create_case(client, seeded_tipo_id)
    response = client.patch(
        f"/cases/{caso['id']}/review",
        json={
            "estado_recontrol": "incorrecto",
            "observacion_recontrol": "El modelo extrajo mal el numero de tramite.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["estado_recontrol"] == "incorrecto"
    assert "numero de tramite" in body["observacion_recontrol"]


def test_revertir_a_pendiente(client: TestClient, seeded_tipo_id: str) -> None:
    caso = _create_case(client, seeded_tipo_id)
    client.patch(
        f"/cases/{caso['id']}/review",
        json={"estado_recontrol": "correcto", "observacion_recontrol": None},
    )
    response = client.patch(
        f"/cases/{caso['id']}/review",
        json={"estado_recontrol": "pendiente", "observacion_recontrol": None},
    )
    assert response.status_code == 200
    assert response.json()["estado_recontrol"] == "pendiente"


def test_marcar_caso_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.patch(
        "/cases/00000000-0000-0000-0000-000000000000/review",
        json={"estado_recontrol": "correcto", "observacion_recontrol": None},
    )
    assert response.status_code == 404


def test_estado_invalido_devuelve_422(client: TestClient, seeded_tipo_id: str) -> None:
    caso = _create_case(client, seeded_tipo_id)
    response = client.patch(
        f"/cases/{caso['id']}/review",
        json={"estado_recontrol": "raro", "observacion_recontrol": None},
    )
    assert response.status_code == 422


def test_filtro_recontrol_en_lista(client: TestClient, seeded_tipo_id: str) -> None:
    caso_a = _create_case(client, seeded_tipo_id)
    caso_b = _create_case(client, seeded_tipo_id)
    client.patch(
        f"/cases/{caso_a['id']}/review",
        json={"estado_recontrol": "incorrecto", "observacion_recontrol": "obs"},
    )

    pendientes = client.get("/cases?recontrol=pendiente").json()
    incorrectos = client.get("/cases?recontrol=incorrecto").json()

    pendientes_ids = {item["id"] for item in pendientes["items"]}
    incorrectos_ids = {item["id"] for item in incorrectos["items"]}

    assert caso_a["id"] in incorrectos_ids
    assert caso_a["id"] not in pendientes_ids
    assert caso_b["id"] in pendientes_ids
