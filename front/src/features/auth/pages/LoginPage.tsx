import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Navigate, useNavigate } from "react-router-dom";
import { Alert } from "@/components/Alert";
import { Button } from "@/components/Button";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { extractApiMessage } from "@/lib/errors";

const schema = z.object({
  email: z.string().email("Email invalido."),
  password: z.string().min(1, "Ingresa la contrasena."),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage(): ReactNode {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const { register, handleSubmit, formState } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  if (loading) return null;
  if (user) return <Navigate to="/casos" replace />;

  async function onSubmit(values: FormValues): Promise<void> {
    setError(null);
    setSubmitting(true);
    try {
      await login(values);
      navigate("/casos");
    } catch (err) {
      setError(extractApiMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <header className="space-y-2 text-center">
          <div className="mx-auto grid h-12 w-12 place-items-center rounded-lg bg-brand-600 text-lg font-semibold text-white">
            A
          </div>
          <h1 className="text-xl font-semibold text-slate-900">Ingresar a ADA</h1>
          <p className="text-xs text-slate-500">
            Plataforma de Auditoria Documental Automatizada
          </p>
        </header>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <label className="block space-y-1">
            <span className="text-xs font-medium text-slate-700">Email</span>
            <input
              type="email"
              {...register("email")}
              placeholder="usuario@dominio.com"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              autoFocus
            />
            {formState.errors.email && (
              <span className="text-xs text-rose-700">{formState.errors.email.message}</span>
            )}
          </label>

          <label className="block space-y-1">
            <span className="text-xs font-medium text-slate-700">Contrasena</span>
            <input
              type="password"
              {...register("password")}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            {formState.errors.password && (
              <span className="text-xs text-rose-700">{formState.errors.password.message}</span>
            )}
          </label>

          {error && (
            <Alert variant="danger" title="No se pudo iniciar sesion">
              {error}
            </Alert>
          )}

          <Button type="submit" loading={submitting} className="w-full">
            Ingresar
          </Button>
        </form>

        <p className="text-center text-xs text-slate-500">
          Usuarios de demostracion: admin@ada.local, entrenador@ada.local, cliente@ada.local
          (contrasena ada2026)
        </p>
      </div>
    </div>
  );
}

