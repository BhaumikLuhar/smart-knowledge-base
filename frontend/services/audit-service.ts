import { apiGet } from "@/lib/api";

import {
  AuditLogResponse,
} from "@/types/audit";

export async function getAuditLogs() {

  return apiGet(
    "/api/v1/admin/audit-logs?limit=100"
  ) as Promise<AuditLogResponse>;

}