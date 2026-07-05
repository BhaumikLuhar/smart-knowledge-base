export interface User {
  id: string;

  full_name: string;

  email: string;

  role: string;

  department_id: string | null;

  department_name: string | null;

  last_login: string | null;

  is_active: boolean;
}

export interface CreateUserRequest {
  full_name: string;

  email: string;

  password: string;

  department_id: string | null;

  role: string;
}

export interface UpdateUserRequest {
  role?: string;

  department_id?: string | null;

  is_active?: boolean;
}