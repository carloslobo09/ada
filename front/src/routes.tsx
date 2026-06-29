import { createBrowserRouter, Navigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/features/auth/components/ProtectedRoute";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { CaseDetailPage } from "@/features/cases/pages/CaseDetailPage";
import { CasesListPage } from "@/features/cases/pages/CasesListPage";
import { ReControlPage } from "@/features/cases/pages/ReControlPage";
import { CreatePromptVersionPage } from "@/features/prompts/pages/CreatePromptVersionPage";
import { PromptVersionDetailPage } from "@/features/prompts/pages/PromptVersionDetailPage";
import { PromptVersionsPage } from "@/features/prompts/pages/PromptVersionsPage";

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
              { path: "re-control", element: <ReControlPage /> },
              { path: "configuracion", element: <PromptVersionsPage /> },
              { path: "configuracion/nueva", element: <CreatePromptVersionPage /> },
              { path: "configuracion/:versionId", element: <PromptVersionDetailPage /> },
            ],
          },
          { path: "*", element: <Navigate to="/casos" replace /> },
        ],
      },
    ],
  },
]);
