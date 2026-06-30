export interface KpiSummary {
  total_casos: number;
  porcentaje_aprobados: number;
  porcentaje_rechazados: number;
  pendientes_recontrol: number;
  porcentaje_acuerdo_ia_humano: number | null;
  confianza_promedio: number | null;
}

export interface DistribucionDecisiones {
  aprobados: number;
  rechazados: number;
  rechazados_pre_llm: number;
}

export interface AcuerdoIaHumano {
  correctos: number;
  incorrectos: number;
  falsos_positivos: number;
  falsos_negativos: number;
  revisados: number;
}

export interface MotivoRechazo {
  motivo: string;
  cantidad: number;
}

export interface CasosPorDia {
  fecha: string;
  cantidad: number;
}

export interface DashboardMetrics {
  kpis: KpiSummary;
  distribucion_decisiones: DistribucionDecisiones;
  acuerdo_ia_humano: AcuerdoIaHumano;
  top_motivos_rechazo: MotivoRechazo[];
  casos_por_dia: CasosPorDia[];
}
