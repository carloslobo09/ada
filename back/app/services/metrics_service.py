from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.models.caso import Caso
from app.models.decision import Decision
from app.schemas.metrics import (
    AcuerdoIaHumano,
    CasosPorDia,
    DashboardMetrics,
    DistribucionDecisiones,
    KpiSummary,
    MotivoRechazo,
)

DEFAULT_WINDOW_DAYS = 7
TOP_MOTIVOS = 5


class MetricsService:
    """Agrega los datos para el dashboard del entrenador.

    Todas las metricas se calculan en SQL sin materializaciones extra. Para
    volumenes mas grandes conviene cachear este JSON o pasarlo a vistas
    materializadas; en el MVP cada llamada agrega en vivo.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def dashboard(
        self,
        *,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> DashboardMetrics:
        rango_hasta = hasta or datetime.now(timezone.utc).date()
        rango_desde = desde or (rango_hasta - timedelta(days=DEFAULT_WINDOW_DAYS - 1))
        if rango_desde > rango_hasta:
            rango_desde = rango_hasta

        inicio = datetime.combine(rango_desde, time.min, tzinfo=timezone.utc)
        fin = datetime.combine(rango_hasta, time.max, tzinfo=timezone.utc)

        self._inicio = inicio
        self._fin = fin

        return DashboardMetrics(
            kpis=self._kpis(),
            distribucion_decisiones=self._distribucion(),
            acuerdo_ia_humano=self._acuerdo(),
            top_motivos_rechazo=self._top_motivos(),
            casos_por_dia=self._casos_por_dia(rango_desde, rango_hasta),
        )

    def _kpis(self) -> KpiSummary:
        total = self._count(self._caso_count_stmt())
        aprobados = self._count_veredicto("approved")
        rechazados = self._count_veredicto("rejected")

        pendientes = self._count(
            self._caso_count_stmt(extra=Caso.estado_recontrol == "pendiente")
        )

        revisados = self._count(
            self._caso_count_stmt(extra=Caso.estado_recontrol != "pendiente")
        )
        correctos = self._count(
            self._caso_count_stmt(extra=Caso.estado_recontrol == "correcto")
        )
        acuerdo = round(correctos / revisados * 100, 1) if revisados else None

        confianza_stmt = (
            select(func.avg(Decision.confianza_global))
            .select_from(Caso)
            .join(Decision, Decision.id == Caso.ref_decision)
            .where(self._caso_in_range())
        )
        confianza = self._session.scalar(confianza_stmt)
        confianza_promedio = round(float(confianza), 2) if confianza is not None else None

        return KpiSummary(
            total_casos=total,
            porcentaje_aprobados=round(aprobados / total * 100, 1) if total else 0.0,
            porcentaje_rechazados=round(rechazados / total * 100, 1) if total else 0.0,
            pendientes_recontrol=pendientes,
            porcentaje_acuerdo_ia_humano=acuerdo,
            confianza_promedio=confianza_promedio,
        )

    def _distribucion(self) -> DistribucionDecisiones:
        aprobados = self._count_veredicto("approved")
        rechazados_pre_llm = self._count(
            self._caso_count_stmt(extra=Caso.estado == "rechazado_pre_llm")
        )
        rechazados_total = self._count_veredicto("rejected")
        rechazados_post_llm = max(0, rechazados_total - rechazados_pre_llm)
        return DistribucionDecisiones(
            aprobados=aprobados,
            rechazados=rechazados_post_llm,
            rechazados_pre_llm=rechazados_pre_llm,
        )

    def _acuerdo(self) -> AcuerdoIaHumano:
        revisados = self._count(
            self._caso_count_stmt(extra=Caso.estado_recontrol != "pendiente")
        )
        correctos = self._count(
            self._caso_count_stmt(extra=Caso.estado_recontrol == "correcto")
        )
        incorrectos = self._count(
            self._caso_count_stmt(extra=Caso.estado_recontrol == "incorrecto")
        )

        falsos_positivos = self._count(
            select(func.count(Caso.id))
            .join(Decision, Decision.id == Caso.ref_decision)
            .where(
                self._caso_in_range(),
                Caso.estado_recontrol == "incorrecto",
                Decision.veredicto == "approved",
            )
        )
        falsos_negativos = self._count(
            select(func.count(Caso.id))
            .join(Decision, Decision.id == Caso.ref_decision)
            .where(
                self._caso_in_range(),
                Caso.estado_recontrol == "incorrecto",
                Decision.veredicto == "rejected",
            )
        )

        return AcuerdoIaHumano(
            correctos=correctos,
            incorrectos=incorrectos,
            falsos_positivos=falsos_positivos,
            falsos_negativos=falsos_negativos,
            revisados=revisados,
        )

    def _top_motivos(self) -> list[MotivoRechazo]:
        stmt = (
            select(Decision.motivos)
            .join(Caso, Caso.ref_decision == Decision.id)
            .where(
                self._caso_in_range(),
                Decision.veredicto == "rejected",
                Decision.motivos.isnot(None),
            )
        )
        motivos_raw = self._session.scalars(stmt).all()
        counter: Counter[str] = Counter()
        for raw in motivos_raw:
            for token in self._parse_motivos(raw or ""):
                counter[token] += 1
        return [
            MotivoRechazo(motivo=name, cantidad=qty)
            for name, qty in counter.most_common(TOP_MOTIVOS)
        ]

    def _casos_por_dia(self, desde: date, hasta: date) -> list[CasosPorDia]:
        stmt = select(Caso.fecha_creacion).where(self._caso_in_range())
        rows = self._session.scalars(stmt).all()
        counter: Counter[str] = Counter()
        for fecha in rows:
            counter[fecha.date().isoformat()] += 1

        serie: list[CasosPorDia] = []
        cursor = desde
        while cursor <= hasta:
            iso = cursor.isoformat()
            serie.append(CasosPorDia(fecha=iso, cantidad=counter.get(iso, 0)))
            cursor += timedelta(days=1)
        return serie

    def _count_veredicto(self, veredicto: str) -> int:
        return self._count(
            select(func.count(Caso.id))
            .join(Decision, Decision.id == Caso.ref_decision)
            .where(self._caso_in_range(), Decision.veredicto == veredicto)
        )

    def _caso_count_stmt(self, *, extra=None) -> Select:
        stmt = select(func.count(Caso.id)).where(self._caso_in_range())
        if extra is not None:
            stmt = stmt.where(extra)
        return stmt

    def _caso_in_range(self):
        return and_(
            Caso.fecha_creacion >= self._inicio,
            Caso.fecha_creacion <= self._fin,
        )

    def _count(self, stmt) -> int:
        return int(self._session.scalar(stmt) or 0)

    @staticmethod
    def _parse_motivos(raw: str) -> list[str]:
        """Extrae el identificador de cada motivo. Formato: 'nombre: detalle | nombre2: detalle | ...'."""
        chunks = [chunk.strip() for chunk in raw.split("|")]
        names: list[str] = []
        for chunk in chunks:
            if not chunk:
                continue
            head, _, _ = chunk.partition(":")
            head = head.strip()
            if head:
                names.append(head)
        return names
