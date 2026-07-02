import { useState, type ReactNode } from "react";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { RecontrolBadge } from "@/features/cases/components/RecontrolBadge";
import { useReviewCase } from "@/features/cases/hooks/useReviewCase";
import type { Case, EstadoRecontrol } from "@/features/cases/types";
import { extractApiMessage } from "@/lib/errors";

interface ReviewPanelProps {
  caso: Case;
}

const OPTIONS: { value: EstadoRecontrol; label: string; description: string }[] = [
  {
    value: "correcto",
    label: "Correcto",
    description: "El analisis automatico del sistema fue acertado.",
  },
  {
    value: "incorrecto",
    label: "Incorrecto",
    description:
      "El analisis se desvio de lo esperado. La observacion alimenta la siguiente version del prompt.",
  },
  {
    value: "pendiente",
    label: "Sin revisar",
    description: "Vuelve el caso a la bandeja del entrenador.",
  },
];

export function ReviewPanel({ caso }: ReviewPanelProps): ReactNode {
  const [estado, setEstado] = useState<EstadoRecontrol>(caso.estado_recontrol);
  const [observacion, setObservacion] = useState(caso.observacion_recontrol ?? "");
  const mutation = useReviewCase();

  function onSubmit(event: React.FormEvent): void {
    event.preventDefault();
    mutation.mutate({
      caseId: caso.id,
      input: {
        estado_recontrol: estado,
        observacion_recontrol: observacion.trim() === "" ? null : observacion.trim(),
      },
    });
  }

  return (
    <section className="space-y-3 rounded-lg border border-slate-200 bg-white p-6">
      <header className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
            Re Control
          </h2>
          <p className="text-xs text-slate-500">
            Revision interna del entrenador sobre el analisis automatico. No modifica la
            decision que ya se entrego al sistema consumidor.
          </p>
        </div>
        <RecontrolBadge estado={caso.estado_recontrol} size="md" />
      </header>

      <form className="space-y-4" onSubmit={onSubmit}>
        <fieldset className="space-y-2">
          {OPTIONS.map((opt) => (
            <label
              key={opt.value}
              className={`flex cursor-pointer items-start gap-3 rounded-md border p-3 transition-colors ${
                estado === opt.value
                  ? "border-brand-400 bg-brand-50"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <input
                type="radio"
                name="estado_recontrol"
                value={opt.value}
                checked={estado === opt.value}
                onChange={() => {
                  mutation.reset();
                  setEstado(opt.value);
                }}
                className="mt-1"
              />
              <div>
                <p className="text-sm font-medium text-slate-900">{opt.label}</p>
                <p className="text-xs text-slate-500">{opt.description}</p>
              </div>
            </label>
          ))}
        </fieldset>

        <label className="block space-y-1">
          <span className="text-xs font-medium text-slate-700">
            Observacion (opcional, hasta 2048 caracteres)
          </span>
          <textarea
            value={observacion}
            onChange={(e) => {
              mutation.reset();
              setObservacion(e.target.value);
            }}
            rows={4}
            maxLength={2048}
            placeholder="Notas para alimentar la siguiente version del prompt..."
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </label>

        {mutation.error && (
          <Alert variant="danger" title="No se pudo guardar la revision">
            {extractApiMessage(mutation.error)}
          </Alert>
        )}
        {mutation.isSuccess && (
          <Alert variant="success">Revision actualizada.</Alert>
        )}

        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-slate-500">
            {caso.fecha_recontrol
              ? `Ultima revision: ${new Date(caso.fecha_recontrol).toLocaleString("es-AR")}`
              : "Aun sin revisar."}
          </p>
          <Button type="submit" loading={mutation.isPending}>
            Guardar revision
          </Button>
        </div>
      </form>
    </section>
  );
}

