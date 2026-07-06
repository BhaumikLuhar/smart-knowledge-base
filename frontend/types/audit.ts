export interface AuditLog {

  id: string;

  user_id: string | null;

  user_email: string | null;

  action: string;

  resource_type: string | null;

  resource_id: string | null;

  details: Record<string, unknown>;

  ip_address: string | null;

  created_at: string;

}

export interface AuditLogResponse {

  total: number;

  limit: number;

  offset: number;

  items: AuditLog[];

}