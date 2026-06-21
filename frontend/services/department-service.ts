import { apiGet } from "@/lib/api";

export async function getDepartments() {
  return apiGet(
    "/api/v1/admin/departments"
  );
}