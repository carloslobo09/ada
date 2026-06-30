import { createBrowserRouter, Navigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/features/auth/components/ProtectedRoute";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { CaseDetailPage } from "@/features/cases/pages/CaseDetailPage";
import { CasesListPage } from "@/features/cases/pages/CasesListPage";
import { TipoDocumentoDetailPage } from "@/features/document-types/pages/TipoDocumentoDetailPage";
import { TiposDocumentoPage } from "@/features/document-types/pages/TiposDocumentoPage";
import { CreatePromptVersionPage } from "@/features/prompts/pages/CreatePromptVersionPage";
import { PromptVersionDetailPage } from "@/features/prompts/pages/PromptVersionDetailPage";
import { UsersPage } from "@/features/users/pages/UsersPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      {
        path: "",
        element: <Layout />,
        children: [
          { index: true, element: <Navigate to="/casos" replace /> },
          { path: "casos", element: <CasesListPage /> },
          { path: "casos/:caseId", element: <CaseDetailPage /> },
          {
            path: "",
            element: <ProtectedRoute allowedRoles={["entrenador", "admin"]} />,
            children: [
              { path: "configuracion", element: <TiposDocumentoPage /> },
              {
                path: "configuracion/tipos/:tipoId",
                element: <TipoDocumentoDetailPage />,
              },
              {
                path: "configuracion/tipos/:tipoId/versiones/nueva",
                element: <CreatePromptVersionPage />,
              },
              {
                path: "configuracion/tipos/:tipoId/versiones/:versionId",
                element: <PromptVersionDetailPage />,
              },
              {
                path: "",
                element: <ProtectedRoute allowedRoles={["admin"]} />,
                children: [
                  { path: "usuarios", element: <UsersPage /> },
                ],
              },
            ],
          },
          { path: "*", element: <Navigate to="/casos" replace /> },
        ],
      },
    ],
  },
]);
