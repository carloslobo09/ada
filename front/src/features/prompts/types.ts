import type {
  CrossValidationResult,
  DecisionStatus,
  RuleResult,
} from "@/features/cases/types";

export type NormalizationType =
  | "trim"
  | "collapse_spaces"
  | "uppercase"
  | "lowercase"
  | "remove_accents"
  | "digits_only";

export const NORMALIZATION_OPTIONS: { value: NormalizationType; label: string }[] = [
  { value: "trim", label: "Trim (espacios al inicio y al final)" },
  { value: "collapse_spaces", label: "Colapsar espacios multiples" },
  { value: "uppercase", label: "Mayusculas" },
  { value: "lowercase", label: "Minusculas" },
  { value: "remove_accents", label: "Quitar acentos" },
  { value: "digits_only", label: "Solo digitos" },
];

export type ComparisonType = "equals" | "fuzzy_60" | "fuzzy_70" | "contains";

export const COMPARISON_OPTIONS: { value: ComparisonType; label: string }[] = [
  { value: "equals", label: "Exacto" },
  { value: "fuzzy_60", label: "Similitud >= 60%" },
  { value: "fuzzy_70", label: "Similitud >= 70%" },
  { value: "contains", label: "Contiene" },
];

export type EstadoPromptVersion = "borrador" | "publicada" | "archivada";

export interface ExtractionField {
  name: string;
  label: string;
}

export interface CrossFieldConfig {
  field: string;
  normalization: NormalizationType[];
  comparison: ComparisonType;
  critical: boolean;
  required_expected: boolean;
}

export interface PromptVersion {
  id: string;
  numero: number;
  tipo_documento_id: string;
  prompt_text: string;
  extraction_fields: ExtractionField[];
  cross_validation_config: CrossFieldConfig[];
  estado: EstadoPromptVersion;
  ref_usuario_creador: string | null;
  ref_usuario_publicador: string | null;
  created_at: string;
  activated_at: string | null;
}

export interface PromptVersionListItem {
  id: string;
  numero: number;
  tipo_documento_id: string;
  estado: EstadoPromptVersion;
  created_at: string;
  activated_at: string | null;
}

export interface CreatePromptVersionInput {
  tipo_documento_id: string;
  prompt_text: string;
  extraction_fields: ExtractionField[];
  cross_validation_config: CrossFieldConfig[];
}

export interface SimulationResult {
  prompt_version_id: string;
  expected_received: Record<string, string> | null;
  raw_extraction: Record<string, unknown> | null;
  normalized_extraction: Record<string, unknown> | null;
  rule_results: RuleResult[] | null;
  cross_validation_results: CrossValidationResult[] | null;
  decision_status: DecisionStatus;
  decision_reason: string;
}

export interface SimulationInput {
  versionId: string;
  file: File;
  expected: Record<string, string> | null;
}
