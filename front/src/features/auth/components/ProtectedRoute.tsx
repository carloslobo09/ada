import type { ReactNode } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { Spinner } from "@/components/Spinner";
import { useAuth } from "@/features/auth/hooks/useAuth";
import type { Rol } from "@/features/auth/types";

interface ProtectedRouteProps {
  allowedRoles?: Rol[];
}

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps): ReactNode {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.rol)) {
    return <Navigate to="/casos" replace />;
  }

  return <Outlet />;
}
