export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  department_id: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}