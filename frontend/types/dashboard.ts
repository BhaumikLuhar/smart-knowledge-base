export interface RecentQuery {
  user: string;
  query: string;
  confidence: string;
  timestamp: string;
}

export interface DashboardSummary {
  total_queries_today: number;

  average_latency_ms: number;

  active_users: number;

  documents_ready: number;

  recent_queries: RecentQuery[];
}


export interface SystemConfig {

  chunk_size: number;

  chunk_overlap: number;

  candidate_top_k: number;

  final_top_k: number;

  max_sessions: number;

}