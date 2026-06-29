import type {
  CrossValidationResult,
  DecisionStatus,
  RuleResult,
} from "@/features/cases/types";

export type ComparisonType =
  | "equals"
  | "equals_normalized"
  | "numeric_equals"
  | "fuzzy_60"
  | "fuzzy_70"
  | "contains";

export const COMPARISON_OPTIONS: { value: ComparisonType; label: string }[] = [
  { value: "equals", label: "Exacto" },
  { value: "equals_normalized", label: "Exacto sin acentos / mayusculas" },
  { value: "numeric_equals", label: "Solo digitos" },
  { value: "fuzzy_60", label: "Similitud >= 60%" },
  { value: "fuzzy_70", label: "Similitud >= 70%" },
  { value: "contains", label: "Contiene" },
];

export type EstadoPromptVersion = "borrador" | "publicada" | "archivada";

export interface CrossFieldConfig {
  field: string;
  comparison: ComparisonType;
  critical: boolean;
  required_expected: boolean;
}

export interface PromptVersion {
  id: string;
  numero: number;
  tipo_documento_id: string;
  prompt_text: string;
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
