"use client";

import { useEffect, useState } from "react";

import ChatSidebar from "@/components/chat/chat-sidebar";
import ChatWindow from "@/components/chat/chat-window";
import ChatInput from "@/components/chat/chat-input";

import {
  createSession,
  getMessages,
  getSessions,
  sendMessage,
} from "@/services/chat-service";

import {
  ChatMessageView,
  ChatSession,
} from "@/types/chat";

export default function ChatPage() {
  const [sessions, setSessions] =
    useState<ChatSession[]>([]);

  const [messages, setMessages] =
    useState<ChatMessageView[]>([]);

  const [activeSessionId, setActiveSessionId] =
    useState<string>();

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function loadSessions() {
    try {
      const response =
        await getSessions();

      setSessions(
        response.sessions
      );

      if (
          response.sessions.length > 0 &&
          !activeSessionId
      ) {
          await loadConversation(
              response.sessions[0].id
          );
      }
    } catch {
      setError(
        "Failed to load sessions."
      );
    }
  }

  async function loadConversation(
    sessionId: string
  ) {
    try {
      setError("");

      const response =
        await getMessages(
          sessionId
        );

      setMessages(
        response.messages
      );

      setActiveSessionId(
        sessionId
      );
    } catch {
      setError(
        "Failed to load conversation."
      );
    }
  }

  async function handleNewChat() {
    try {
      const session =
        await createSession();

      await loadSessions();

      setMessages([]);

      setActiveSessionId(
        session.id
      );

      return session.id;
    } catch {
      setError(
        "Unable to create chat."
      );
    }
  }

  async function handleSend(
    content: string
  ) {
    let sessionId = activeSessionId;
    if (!sessionId) {
      sessionId = await handleNewChat();
    }

    const optimisticMessage: ChatMessageView =
      {
        id: crypto.randomUUID(),
        role: "user",
        content,
        metadata: {},
        created_at:
          new Date().toISOString(),
      };

    setMessages(
      (previous) => [
        ...previous,
        optimisticMessage,
      ]
    );

    setLoading(true);

    setError("");

    try {
      const response =
        await sendMessage(
          content,
          sessionId
        );

      setMessages(
        (previous) => [
          ...previous,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content:
              response.answer,
            metadata: {
              citations:
                response.citations,
              confidence_level:
                response.confidence_level,
              confidence_score:
                response.confidence_score,
              trace:
                response.trace,
            },
            created_at:
              new Date().toISOString(),
          },
        ]
      );

      if (
        response.session_id !==
        activeSessionId
      ) {
        setActiveSessionId(
          response.session_id
        );
      }

      await loadSessions();
    } catch {
      setError(
        "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSessions();
  }, []);

  return (
    <div className="flex h-[calc(100vh-2rem)] border rounded-lg overflow-hidden">

      <ChatSidebar
        sessions={sessions}
        activeSessionId={
          activeSessionId
        }
        onSelect={
          loadConversation
        }
        onNewChat={
          handleNewChat
        }
        disabled={loading}
      />

      <div className="flex flex-col flex-1">

        <ChatWindow
          messages={messages}
          loading={loading}
          error={error}
        />

        <ChatInput
          disabled={loading}
          onSend={
            handleSend
          }
        />

      </div>

    </div>
  );
}