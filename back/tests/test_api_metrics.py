import io
import json
from datetime import date

from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def _post_case(client: TestClient, tipo_id: str, *, expected: dict | None = None):
    data: dict = {"tipo_documento_id": tipo_id}
    if expected is not None:
        data["expected"] = json.dumps(expected)
    return client.post(
        "/cases",
        files={"file": ("dni.png", io.BytesIO(b"x"), "image/png")},
        data=data,
    )


# Payload completo (los tres criticos son obligatorios) con el numero incorrecto,
# para forzar un rechazo por validacion cruzada y no un rechazo pre-LLM.
EXPECTED_NUMERO_INCORRECTO = {
    "numero_dni": "99999999",
    "nombre_completo": "LOBO CARLOS IGNACIO",
    "fecha_nacimiento": "1997-08-15",
}


def test_dashboard_cliente_devuelve_403(client: TestClient, cliente_token: str) -> None:
    response = client.get("/metrics/dashboard", headers=auth_headers(cliente_token))
    assert response.status_code == 403


def test_dashboard_vacio_devuelve_ceros(client: TestClient) -> None:
    body = client.get("/metrics/dashboard").json()
    assert body["kpis"]["total_casos"] == 0
    assert body["kpis"]["porcentaje_acuerdo_ia_humano"] is None
    assert body["distribucion_decisiones"]["aprobados"] == 0
    assert body["top_motivos_rechazo"] == []
    assert len(body["casos_por_dia"]) == 7


def test_dashboard_cuenta_casos_y_distribucion(
    client: TestClient, seeded_tipo_id: str
) -> None:
    _post_case(client, seeded_tipo_id)
    _post_case(client, seeded_tipo_id, expected=EXPECTED_NUMERO_INCORRECTO)

    body = client.get("/metrics/dashboard").json()
    kpis = body["kpis"]
    assert kpis["total_casos"] == 2
    assert kpis["porcentaje_aprobados"] == 50.0
    assert kpis["porcentaje_rechazados"] == 50.0
    assert kpis["pendientes_recontrol"] == 2

    dist = body["distribucion_decisiones"]
    assert dist["aprobados"] == 1
    assert dist["rechazados"] == 1
    assert dist["rechazados_pre_llm"] == 0


def test_top_motivos_conserva_el_campo_del_cross(
    client: TestClient, seeded_tipo_id: str
) -> None:
    _post_case(client, seeded_tipo_id, expected=EXPECTED_NUMERO_INCORRECTO)

    body = client.get("/metrics/dashboard").json()
    motivos = [m["motivo"] for m in body["top_motivos_rechazo"]]
    assert "cross:numero_dni" in motivos


def test_acuerdo_ia_humano_y_falsos_positivos(
    client: TestClient, seeded_tipo_id: str
) -> None:
    aprobado = _post_case(client, seeded_tipo_id).json()
    rechazado = _post_case(
        client, seeded_tipo_id, expected=EXPECTED_NUMERO_INCORRECTO
    ).json()

    client.patch(
        f"/cases/{aprobado['id']}/review",
        json={"estado_recontrol": "incorrecto", "observacion_recontrol": "fallo"},
    )
    client.patch(
        f"/cases/{rechazado['id']}/review",
        json={"estado_recontrol": "correcto", "observacion_recontrol": None},
    )

    body = client.get("/metrics/dashboard").json()
    acuerdo = body["acuerdo_ia_humano"]
    assert acuerdo["revisados"] == 2
    assert acuerdo["correctos"] == 1
    assert acuerdo["incorrectos"] == 1
    # la IA habia aprobado y el humano marco incorrecto
    assert acuerdo["falsos_positivos"] == 1
    assert acuerdo["falsos_negativos"] == 0
    assert body["kpis"]["porcentaje_acuerdo_ia_humano"] == 50.0


def test_filtro_de_fechas_excluye_casos_fuera_del_rango(
    client: TestClient, seeded_tipo_id: str
) -> None:
    _post_case(client, seeded_tipo_id)

    hoy = date.today().isoformat()
    en_rango = client.get(
        f"/metrics/dashboard?desde={hoy}&hasta={hoy}"
    ).json()
    assert en_rango["kpis"]["total_casos"] == 1
    assert len(en_rango["casos_por_dia"]) == 1

    fuera = client.get(
        "/metrics/dashboard?desde=2020-01-01&hasta=2020-01-07"
    ).json()
    assert fuera["kpis"]["total_casos"] == 0
