export interface DepartmentBreakdown {
  department: string;
  query_count: number;
  percentage: number;
}

export interface HourlyQueryVolume {
  hour: number;
  query_count: number;
}

export interface RecentQuery {
  user: string;
  query: string;
  confidence: string;
  timestamp: string;
}

export interface DashboardSummary {

  total_queries_today: number;

  today_errors: number;

  average_latency_ms: number;

  average_tokens: number;

  total_documents: number;

  documents_ready: number;

  active_users: number;

  permission_denials_today: number;

  retrieval_precision_avg: number;

  department_breakdown: DepartmentBreakdown[];

  hourly_query_volume: HourlyQueryVolume[];

  recent_queries: RecentQuery[];

}

export interface SystemConfig {

  chunk_size: number;

  chunk_overlap: number;

  candidate_top_k: number;

  final_top_k: number;

  max_sessions: number;

}