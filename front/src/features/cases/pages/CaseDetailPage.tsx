import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Spinner } from "@/components/Spinner";
import { useGetCase } from "@/features/cases/hooks/useGetCase";
import { CaseResultPanel } from "@/features/cases/components/CaseResultPanel";
import { ReviewPanel } from "@/features/cases/components/ReviewPanel";

export function CaseDetailPage(): ReactNode {
  const { caseId } = useParams<{ caseId: string }>();
  const { data, isLoading, isError, error } = useGetCase(caseId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Alert variant="danger" title="No se pudo cargar el caso">
        {error instanceof Error ? error.message : "Caso no encontrado."}
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Link to="/casos" className="text-sm text-brand-700 hover:underline">
        ← Volver a la lista
      </Link>
      <CaseResultPanel caso={data} />
      <ReviewPanel caso={data} />
    </div>
  );
}
