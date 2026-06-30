import io

from fastapi.testclient import TestClient

from tests.conftest import (
    ADMIN_EMAIL,
    CLIENTE_EMAIL,
    ENTRENADOR_EMAIL,
    SEED_PASSWORD,
    auth_headers,
)


def _login(client: TestClient, email: str, password: str):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_login_admin_devuelve_token_y_user(client: TestClient) -> None:
    response = _login(client, ADMIN_EMAIL, SEED_PASSWORD)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == ADMIN_EMAIL
    assert body["user"]["rol"] == "admin"


def test_login_cliente_devuelve_rol_cliente(client: TestClient) -> None:
    body = _login(client, CLIENTE_EMAIL, SEED_PASSWORD).json()
    assert body["user"]["rol"] == "cliente"


def test_login_password_incorrecto_devuelve_401(client: TestClient) -> None:
    response = _login(client, ADMIN_EMAIL, "incorrecta")
    assert response.status_code == 401


def test_login_email_inexistente_devuelve_401(client: TestClient) -> None:
    response = _login(client, "noexiste@ada.local", SEED_PASSWORD)
    assert response.status_code == 401


def test_me_con_token_devuelve_usuario(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == ADMIN_EMAIL


def test_me_sin_token_devuelve_401(anon_client: TestClient) -> None:
    response = anon_client.get("/auth/me")
    assert response.status_code == 401


def test_me_con_token_invalido_devuelve_401(anon_client: TestClient) -> None:
    response = anon_client.get(
        "/auth/me", headers={"Authorization": "Bearer no-es-un-jwt"}
    )
    assert response.status_code == 401


def test_endpoint_protegido_sin_token_devuelve_401(anon_client: TestClient) -> None:
    response = anon_client.get("/cases")
    assert response.status_code == 401


def test_cliente_puede_crear_caso(
    client: TestClient, cliente_token: str, seeded_tipo_id: str
) -> None:
    response = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(cliente_token),
    )
    assert response.status_code == 201


def test_cliente_solo_ve_sus_casos(
    client: TestClient,
    cliente_token: str,
    entrenador_token: str,
    seeded_tipo_id: str,
) -> None:
    caso_cliente = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(cliente_token),
    ).json()
    caso_entrenador = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(entrenador_token),
    ).json()

    listado_cliente = client.get(
        "/cases", headers=auth_headers(cliente_token)
    ).json()
    ids_cliente = {item["id"] for item in listado_cliente["items"]}
    assert caso_cliente["id"] in ids_cliente
    assert caso_entrenador["id"] not in ids_cliente


def test_cliente_no_puede_ver_caso_ajeno(
    client: TestClient,
    cliente_token: str,
    entrenador_token: str,
    seeded_tipo_id: str,
) -> None:
    caso = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(entrenador_token),
    ).json()
    response = client.get(
        f"/cases/{caso['id']}", headers=auth_headers(cliente_token)
    )
    assert response.status_code == 404


def test_cliente_recibe_vista_resumida(
    client: TestClient, cliente_token: str, seeded_tipo_id: str
) -> None:
    caso = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(cliente_token),
    ).json()
    # campos visibles
    assert "id" in caso
    assert "fecha_creacion" in caso
    assert "estado" in caso
    assert "veredicto" in caso
    assert "motivos" in caso
    assert "campos_extraidos" in caso
    assert "documento" in caso
    # campos internos NO visibles
    assert "ref_documento" not in caso
    assert "ref_decision" not in caso
    assert "ref_usuario_cliente" not in caso
    assert "ref_usuario_recontrol" not in caso
    assert "estado_recontrol" not in caso
    assert "decision" not in caso
    # documento light, sin hash ni ruta interna
    documento = caso["documento"]
    assert "nombre_archivo" in documento
    assert "hash_integridad" not in documento
    assert "ubicacion_s3" not in documento
    assert "tipo_documento_id" not in documento


def test_entrenador_recibe_vista_completa(
    client: TestClient, entrenador_token: str, seeded_tipo_id: str
) -> None:
    caso = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(entrenador_token),
    ).json()
    assert "ref_documento" in caso
    assert "ref_decision" in caso
    assert "estado_recontrol" in caso
    assert "decision" in caso
    assert "documento" in caso
    assert caso["documento"]["hash_integridad"]


def test_listado_cliente_no_expone_estado_recontrol(
    client: TestClient, cliente_token: str, seeded_tipo_id: str
) -> None:
    client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(cliente_token),
    )
    listado = client.get("/cases", headers=auth_headers(cliente_token)).json()
    assert len(listado["items"]) >= 1
    item = listado["items"][0]
    assert "veredicto" in item
    assert "estado_recontrol" not in item
    assert "decision" not in item


def test_cliente_no_puede_revisar(
    client: TestClient, cliente_token: str, seeded_tipo_id: str
) -> None:
    caso = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(cliente_token),
    ).json()
    response = client.patch(
        f"/cases/{caso['id']}/review",
        json={"estado_recontrol": "correcto", "observacion_recontrol": None},
        headers=auth_headers(cliente_token),
    )
    assert response.status_code == 403


def test_entrenador_puede_revisar(
    client: TestClient, entrenador_token: str, seeded_tipo_id: str
) -> None:
    caso = client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data={"tipo_documento_id": seeded_tipo_id},
        headers=auth_headers(entrenador_token),
    ).json()
    response = client.patch(
        f"/cases/{caso['id']}/review",
        json={"estado_recontrol": "correcto", "observacion_recontrol": None},
        headers=auth_headers(entrenador_token),
    )
    assert response.status_code == 200


def test_cliente_no_puede_crear_prompt_version(
    client: TestClient, cliente_token: str, seeded_tipo_id: str
) -> None:
    response = client.post(
        "/prompt-versions",
        json={
            "tipo_documento_id": seeded_tipo_id,
            "prompt_text": "Prompt",
            "extraction_fields": [{"name": "campo", "label": "Campo"}],
            "cross_validation_config": [],
        },
        headers=auth_headers(cliente_token),
    )
    assert response.status_code == 403


def test_entrenador_puede_crear_prompt_version(
    client: TestClient, entrenador_token: str, seeded_tipo_id: str
) -> None:
    response = client.post(
        "/prompt-versions",
        json={
            "tipo_documento_id": seeded_tipo_id,
            "prompt_text": "Prompt v2",
            "extraction_fields": [{"name": "campo", "label": "Campo"}],
            "cross_validation_config": [],
        },
        headers=auth_headers(entrenador_token),
    )
    assert response.status_code == 201


def test_cliente_no_puede_crear_tipo_documento(
    client: TestClient, cliente_token: str
) -> None:
    response = client.post(
        "/document-types",
        json={"nombre": "Pasaporte", "descripcion": "x"},
        headers=auth_headers(cliente_token),
    )
    assert response.status_code == 403


def test_entrenador_no_puede_crear_tipo_documento(
    client: TestClient, entrenador_token: str
) -> None:
    response = client.post(
        "/document-types",
        json={"nombre": "Pasaporte", "descripcion": "x"},
        headers=auth_headers(entrenador_token),
    )
    assert response.status_code == 403


def test_cliente_puede_listar_prompt_versions(
    client: TestClient, cliente_token: str
) -> None:
    response = client.get("/prompt-versions", headers=auth_headers(cliente_token))
    assert response.status_code == 200
