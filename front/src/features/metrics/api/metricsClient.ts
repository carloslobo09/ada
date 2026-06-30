import { apiClient } from "@/lib/apiClient";
import type { DashboardMetrics } from "@/features/metrics/types";

export interface DashboardRange {
  desde: string;
  hasta: string;
}

export async function getDashboardMetrics(
  range: DashboardRange,
): Promise<DashboardMetrics> {
  const response = await apiClient.get<DashboardMetrics>("/metrics/dashboard", {
    params: { desde: range.desde, hasta: range.hasta },
  });
  return response.data;
}
