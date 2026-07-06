export interface Citation {
  document_name: string;
  page_numbers: number[];
  section_references: string[];
  chunk_indexes: number[];
  department_id: string | null;
  chunk_excerpt: string;
}

export interface TraceStep {

  agent_name: string;

  input_summary: string;

  output_summary: string;

  latency: number;

}

export interface ChatResponse {
  session_id: string;

  answer: string;

  citations: Citation[];

  confidence_score: number;

  confidence_level:
    | "low"
    | "medium"
    | "high";

  tokens_used: number;

  fallback: boolean;

  model_used: string | null;

  trace: TraceStep[];
}

export interface ChatSession {
  id: string;

  created_at: string;

  last_active: string;

  last_message_role: string | null;

  last_message: string | null;

  last_message_at: string | null;
}

export interface ChatSessionListResponse {
  sessions: ChatSession[];
}

export interface ChatMessage {
  id: string;

  role: "user" | "assistant";

  content: string;

  metadata: Record<
    string,
    unknown
  >;

  created_at: string;
}

export interface ChatMessagesResponse {
  session_id: string;

  messages: ChatMessage[];
}

export interface CreateSessionResponse {
  id: string;

  created_at: string;

  last_active: string;
}


export interface ChatMessageView {
  id: string;

  role: "user" | "assistant";

  content: string;

  metadata: Record<string, unknown>;

  created_at: string;
}