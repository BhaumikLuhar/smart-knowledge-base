import { apiGet } from "@/lib/api";

import {
  DashboardSummary,
} from "@/types/dashboard";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiGet(
    "/api/v1/admin/metrics/summary"
  );
}

export async function getSystemConfig() {

  return apiGet(
    "/api/v1/admin/config"
  );

}