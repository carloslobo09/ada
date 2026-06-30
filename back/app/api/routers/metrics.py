from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db import get_session
from app.models.usuario import Usuario
from app.schemas.metrics import DashboardMetrics
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])

EntrenadorOAdmin = Annotated[Usuario, Depends(require_roles("entrenador", "admin"))]


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(
    actor: EntrenadorOAdmin,
    session: Annotated[Session, Depends(get_session)],
    desde: Annotated[
        date | None,
        Query(description="Fecha desde, inclusive (YYYY-MM-DD). Default: hasta menos 6 dias."),
    ] = None,
    hasta: Annotated[
        date | None,
        Query(description="Fecha hasta, inclusive (YYYY-MM-DD). Default: hoy."),
    ] = None,
) -> DashboardMetrics:
    return MetricsService(session).dashboard(desde=desde, hasta=hasta)
