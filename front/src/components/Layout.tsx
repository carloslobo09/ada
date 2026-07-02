import { NavLink, Outlet, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { ROL_LABEL, type Rol } from "@/features/auth/types";

interface NavItem {
  to: string;
  label: string;
  allowedRoles?: Rol[];
}

function buildNav(rol: Rol | undefined): NavItem[] {
  const casosLabel = rol === "cliente" ? "Mis casos" : "Re Control";
  return [
    { to: "/casos", label: casosLabel },
    { to: "/configuracion", label: "Configuracion", allowedRoles: ["entrenador", "admin"] },
    { to: "/usuarios", label: "Usuarios", allowedRoles: ["admin"] },
  ];
}

export function Layout(): ReactNode {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout(): void {
    logout();
    navigate("/login");
  }

  const nav = buildNav(user?.rol).filter(
    (item) => !item.allowedRoles || (user && item.allowedRoles.includes(user.rol)),
  );

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600 text-white font-semibold">
              A
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">ADA</p>
              <p className="text-xs text-slate-500">Auditoria Documental Automatizada</p>
            </div>
          </div>
          <nav className="flex gap-1">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          {user && (
            <div className="flex items-center gap-3">
              <div className="text-right text-xs">
                <p className="font-medium text-slate-900">{user.nombre}</p>
                <p className="text-slate-500">{ROL_LABEL[user.rol]}</p>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                Salir
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 bg-white py-4">
        <div className="mx-auto max-w-5xl px-6 text-xs text-slate-500">
          ADA MVP - Prototipo de Trabajo Final de Graduacion, Universidad Siglo 21
        </div>
      </footer>
    </div>
  );
}
