import { useQuery } from "@tanstack/react-query";
import {
  getDashboardMetrics,
  type DashboardRange,
} from "@/features/metrics/api/metricsClient";

export function useDashboardMetrics(range: DashboardRange) {
  return useQuery({
    queryKey: ["metrics", "dashboard", range.desde, range.hasta],
    queryFn: () => getDashboardMetrics(range),
  });
}
