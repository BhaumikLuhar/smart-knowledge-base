import {
  apiGet,
  apiPost,
  apiPut,
} from "@/lib/api";

import {
  CreateUserRequest,
  UpdateUserRequest,
  User,
} from "@/types/user";

export async function getUsers(): Promise<User[]> {
  return apiGet(
    "/api/v1/admin/users"
  );
}

export async function createUser(
  payload: CreateUserRequest
): Promise<User> {
  return apiPost(
    "/api/v1/admin/users",
    payload
  );
}

export async function updateUser(
  id: string,
  payload: UpdateUserRequest
): Promise<User> {
  return apiPut(
    `/api/v1/admin/users/${id}`,
    payload
  );
}