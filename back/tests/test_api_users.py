from fastapi.testclient import TestClient

from tests.conftest import (
    ADMIN_EMAIL,
    CLIENTE_EMAIL,
    SEED_PASSWORD,
    auth_headers,
)


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    response.raise_for_status()
    return response.json()["access_token"]


def test_list_users_admin_ve_los_seed(client: TestClient) -> None:
    response = client.get("/users")
    assert response.status_code == 200
    emails = {u["email"] for u in response.json()}
    assert ADMIN_EMAIL in emails
    assert CLIENTE_EMAIL in emails


def test_list_users_cliente_devuelve_403(
    client: TestClient, cliente_token: str
) -> None:
    response = client.get("/users", headers=auth_headers(cliente_token))
    assert response.status_code == 403


def test_create_user(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "email": "nuevo@ada.local",
            "nombre": "Usuario Nuevo",
            "rol": "entrenador",
            "password": "secreto123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "nuevo@ada.local"
    assert body["rol"] == "entrenador"
    assert body["estado"] == "activo"

    token = _login(client, "nuevo@ada.local", "secreto123")
    assert token


def test_create_user_email_duplicado_devuelve_409(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "email": ADMIN_EMAIL,
            "nombre": "Otro",
            "rol": "admin",
            "password": "secreto123",
        },
    )
    assert response.status_code == 409


def test_create_user_password_corta_devuelve_422(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "email": "corto@ada.local",
            "nombre": "Test",
            "rol": "cliente",
            "password": "abc",
        },
    )
    assert response.status_code == 422


def test_update_user_cambia_nombre_y_rol(client: TestClient) -> None:
    users = client.get("/users").json()
    cliente_id = next(u["id"] for u in users if u["email"] == CLIENTE_EMAIL)
    response = client.patch(
        f"/users/{cliente_id}",
        json={"nombre": "Cliente Renombrado", "rol": "entrenador"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == "Cliente Renombrado"
    assert body["rol"] == "entrenador"


def test_update_user_desactivar(client: TestClient) -> None:
    users = client.get("/users").json()
    cliente_id = next(u["id"] for u in users if u["email"] == CLIENTE_EMAIL)
    response = client.patch(f"/users/{cliente_id}", json={"estado": "inactivo"})
    assert response.status_code == 200
    assert response.json()["estado"] == "inactivo"

    login_response = client.post(
        "/auth/login", json={"email": CLIENTE_EMAIL, "password": SEED_PASSWORD}
    )
    assert login_response.status_code == 403


def test_admin_no_puede_modificarse_a_si_mismo(client: TestClient) -> None:
    users = client.get("/users").json()
    admin_id = next(u["id"] for u in users if u["email"] == ADMIN_EMAIL)
    response = client.patch(f"/users/{admin_id}", json={"rol": "cliente"})
    assert response.status_code == 403


def test_admin_no_puede_resetearse_a_si_mismo(client: TestClient) -> None:
    users = client.get("/users").json()
    admin_id = next(u["id"] for u in users if u["email"] == ADMIN_EMAIL)
    response = client.post(
        f"/users/{admin_id}/reset-password",
        json={"new_password": "nuevopass123"},
    )
    assert response.status_code == 403


def test_reset_password_de_otro_usuario(client: TestClient) -> None:
    users = client.get("/users").json()
    cliente_id = next(u["id"] for u in users if u["email"] == CLIENTE_EMAIL)
    response = client.post(
        f"/users/{cliente_id}/reset-password",
        json={"new_password": "nuevopass123"},
    )
    assert response.status_code == 200

    # La contrasena vieja ya no funciona
    old_response = client.post(
        "/auth/login", json={"email": CLIENTE_EMAIL, "password": SEED_PASSWORD}
    )
    assert old_response.status_code == 401

    # La nueva si
    new_response = client.post(
        "/auth/login", json={"email": CLIENTE_EMAIL, "password": "nuevopass123"}
    )
    assert new_response.status_code == 200


def test_create_user_cliente_devuelve_403(
    client: TestClient, cliente_token: str
) -> None:
    response = client.post(
        "/users",
        json={
            "email": "hack@ada.local",
            "nombre": "Hack",
            "rol": "admin",
            "password": "secreto123",
        },
        headers=auth_headers(cliente_token),
    )
    assert response.status_code == 403
