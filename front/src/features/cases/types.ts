export type Veredicto = "approved" | "rejected";
export type DecisionStatus = Veredicto;
export type EstadoRecontrol = "pendiente" | "correcto" | "incorrecto";

export interface RuleResult {
  name: string;
  severity: "critical" | "informative";
  passed: boolean;
  reason: string;
}

export interface CrossValidationResult {
  field: string;
  expected: string;
  extracted: string;
  comparison: string;
  critical: boolean;
  passed: boolean;
  reason: string;
}

export interface SalidaModelo {
  ref_version_prompt: string;
  contenido_raw: Record<string, unknown>;
}

export interface ResultadoExtraccion {
  campos_normalizados: Record<string, unknown>;
  confianza_por_campo: Record<string, number>;
}

export interface RefsEvidencias {
  salida_modelo: SalidaModelo;
  resultado_extraccion: ResultadoExtraccion;
  evaluacion_reglas: RuleResult[];
}

export interface Documento {
  id: string;
  tipo_documento_id: string;
  ubicacion_s3: string;
  hash_integridad: string;
  fecha_recepcion: string;
  content_type: string;
  file_size: number;
}

export interface Decision {
  id: string;
  veredicto: Veredicto;
  motivos: string;
  confianza_global: number | null;
  refs_evidencias: RefsEvidencias | null;
  expected_received: Record<string, string> | null;
  cross_validation_results: CrossValidationResult[] | null;
  fecha_creacion: string;
}

export interface Case {
  id: string;
  fecha_creacion: string;
  estado: string;
  ref_documento: string | null;
  ref_decision: string | null;
  ref_usuario_cliente: string | null;
  documento: Documento | null;
  decision: Decision | null;
  estado_recontrol: EstadoRecontrol;
  observacion_recontrol: string | null;
  ref_usuario_recontrol: string | null;
  fecha_recontrol: string | null;
}

export interface CasesListItem {
  id: string;
  fecha_creacion: string;
  estado: string;
  estado_recontrol: EstadoRecontrol;
  decision: Decision | null;
}

export interface CasesPage {
  items: CasesListItem[];
  limit: number;
  offset: number;
}

export interface ReviewInput {
  estado_recontrol: EstadoRecontrol;
  observacion_recontrol: string | null;
}
