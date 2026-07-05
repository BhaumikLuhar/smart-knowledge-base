import {
  apiGet,
  apiPost,
} from "@/lib/api";

import {
  ChatMessagesResponse,
  ChatResponse,
  ChatSessionListResponse,
  CreateSessionResponse,
} from "@/types/chat";

export async function sendMessage(
  message: string,
  sessionId?: string
): Promise<ChatResponse> {
  return apiPost(
    "/api/v1/chat/query",
    {
      message,
      session_id:
        sessionId ?? null,
    }
  );
}

export async function createSession(): Promise<CreateSessionResponse> {
  return apiPost(
    "/api/v1/chat/sessions",
    {}
  );
}

export async function getSessions(): Promise<ChatSessionListResponse> {
  return apiGet(
    "/api/v1/chat/sessions"
  );
}

export async function getMessages(
  sessionId: string
): Promise<ChatMessagesResponse> {
  return apiGet(
    `/api/v1/chat/sessions/${sessionId}/messages`
  );
}