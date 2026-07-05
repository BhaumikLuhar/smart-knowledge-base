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


export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  department_id: string | null;
  department_name: string | null;
  is_active: boolean;
}