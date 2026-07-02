from fastapi.testclient import TestClient


def test_seed_inserta_dni_argentino(client: TestClient) -> None:
    response = client.get("/document-types")
    assert response.status_code == 200
    tipos = response.json()
    assert any(
        t["nombre"] == "DNI Argentino" and t["estado"] == "activo" for t in tipos
    )


def test_get_tipo_por_id(client: TestClient, seeded_tipo_id: str) -> None:
    response = client.get(f"/document-types/{seeded_tipo_id}")
    assert response.status_code == 200
    assert response.json()["nombre"] == "DNI Argentino"


def test_get_tipo_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.get("/document-types/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_tipo(client: TestClient) -> None:
    response = client.post(
        "/document-types",
        json={"nombre": "Pasaporte Argentino", "descripcion": "Pasaporte emitido por el RENAPER."},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Pasaporte Argentino"
    assert body["slug"] == "pasaporte-argentino"
    assert body["estado"] == "activo"


def test_create_tipo_duplicado_devuelve_409(client: TestClient) -> None:
    response = client.post(
        "/document-types",
        json={"nombre": "DNI Argentino", "descripcion": "Duplicado"},
    )
    assert response.status_code == 409


def test_patch_tipo(client: TestClient, seeded_tipo_id: str) -> None:
    response = client.patch(
        f"/document-types/{seeded_tipo_id}",
        json={"descripcion": "Descripcion actualizada."},
    )
    assert response.status_code == 200
    assert response.json()["descripcion"] == "Descripcion actualizada."


def test_filtrar_solo_activos(client: TestClient, seeded_tipo_id: str) -> None:
    client.patch(f"/document-types/{seeded_tipo_id}", json={"estado": "inactivo"})
    response = client.get("/document-types?solo_activos=true")
    assert response.status_code == 200
    nombres = [t["nombre"] for t in response.json()]
    assert "DNI Argentino" not in nombres


def test_renombrar_tipo_no_cambia_el_slug(
    client: TestClient, seeded_tipo_id: str
) -> None:
    response = client.patch(
        f"/document-types/{seeded_tipo_id}", json={"nombre": "DNI Renombrado"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == "DNI Renombrado"
    assert body["slug"] == "dni-argentino"


def test_delete_tipo_con_versiones_devuelve_409(
    client: TestClient, seeded_tipo_id: str
) -> None:
    response = client.delete(f"/document-types/{seeded_tipo_id}")
    assert response.status_code == 409


def test_delete_tipo_sin_versiones_funciona(client: TestClient) -> None:
    created = client.post(
        "/document-types",
        json={"nombre": "Tipo Temporal", "descripcion": "Para borrar."},
    ).json()
    response = client.delete(f"/document-types/{created['id']}")
    assert response.status_code == 204


def test_tipo_inactivo_rechaza_casos_nuevos(
    client: TestClient, seeded_tipo_id: str
) -> None:
    import io

    client.patch(f"/document-types/{seeded_tipo_id}", json={"estado": "inactivo"})
    response = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
    )
    assert response.status_code == 409
