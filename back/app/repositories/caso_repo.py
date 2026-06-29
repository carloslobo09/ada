from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.caso import Caso


class CasoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_recibido(self, ref_usuario_cliente: str | None = None) -> Caso:
        caso = Caso(estado="recibido", ref_usuario_cliente=ref_usuario_cliente)
        self._session.add(caso)
        self._session.commit()
        self._session.refresh(caso)
        return caso

    def attach_documento_y_decision(
        self,
        caso: Caso,
        *,
        ref_documento: str,
        ref_decision: str,
        estado: str,
    ) -> Caso:
        caso.ref_documento = ref_documento
        caso.ref_decision = ref_decision
        caso.estado = estado
        self._session.commit()
        self._session.refresh(caso)
        return caso

    def mark_review(
        self,
        caso: Caso,
        *,
        estado_recontrol: str,
        observacion_recontrol: str | None,
        ref_usuario_recontrol: str | None = None,
    ) -> Caso:
        caso.estado_recontrol = estado_recontrol
        caso.observacion_recontrol = observacion_recontrol
        caso.ref_usuario_recontrol = ref_usuario_recontrol
        caso.fecha_recontrol = datetime.now(timezone.utc)
        self._session.commit()
        self._session.refresh(caso)
        return caso

    def get(self, caso_id: str) -> Caso | None:
        return self._session.get(Caso, caso_id)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        estado_recontrol: str | None = None,
        ref_usuario_cliente: str | None = None,
    ) -> list[Caso]:
        stmt = select(Caso).order_by(Caso.fecha_creacion.desc()).limit(limit).offset(offset)
        if estado_recontrol:
            stmt = stmt.where(Caso.estado_recontrol == estado_recontrol)
        if ref_usuario_cliente:
            stmt = stmt.where(Caso.ref_usuario_cliente == ref_usuario_cliente)
        return list(self._session.scalars(stmt))

    def count(self) -> int:
        return int(self._session.scalar(select(func.count(Caso.id))) or 0)
