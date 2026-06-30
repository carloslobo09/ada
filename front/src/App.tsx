import type { ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { ConfirmProvider } from "@/contexts/ConfirmContext";
import { AuthProvider } from "@/features/auth/context/AuthContext";
import { queryClient } from "@/lib/queryClient";
import { router } from "@/routes";

export function App(): ReactNode {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ConfirmProvider>
          <RouterProvider router={router} />
        </ConfirmProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
