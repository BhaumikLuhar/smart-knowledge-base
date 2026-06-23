import {
  apiGet,
  apiUpload,
} from "@/lib/api";

export async function getDocuments() {
  return apiGet(
    "/api/v1/admin/documents"
  );
}


export async function getDocument(
  documentId: string
) {
  return apiGet(
    `/api/v1/admin/documents/${documentId}`
  );
}


export async function uploadDocument(
  formData: FormData
) {
  return apiUpload(
    "/api/v1/admin/documents",
    formData
  );
}