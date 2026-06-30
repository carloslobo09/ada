from pydantic import BaseModel


class KpiSummary(BaseModel):
    total_casos: int
    porcentaje_aprobados: float
    porcentaje_rechazados: float
    pendientes_recontrol: int
    porcentaje_acuerdo_ia_humano: float | None
    confianza_promedio: float | None


class DistribucionDecisiones(BaseModel):
    aprobados: int
    rechazados: int
    rechazados_pre_llm: int


class AcuerdoIaHumano(BaseModel):
    correctos: int
    incorrectos: int
    falsos_positivos: int
    falsos_negativos: int
    revisados: int


class MotivoRechazo(BaseModel):
    motivo: str
    cantidad: int


class CasosPorDia(BaseModel):
    fecha: str
    cantidad: int


class DashboardMetrics(BaseModel):
    kpis: KpiSummary
    distribucion_decisiones: DistribucionDecisiones
    acuerdo_ia_humano: AcuerdoIaHumano
    top_motivos_rechazo: list[MotivoRechazo]
    casos_por_dia: list[CasosPorDia]
