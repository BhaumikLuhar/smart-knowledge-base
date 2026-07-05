"use client";

import { useEffect, useRef } from "react";
import MessageBubble from "./message-bubble";
import TypingIndicator from "./typing-indicator";

import { ChatMessage } from "@/types/chat";

interface Props {
  messages: ChatMessage[];

  loading: boolean;

  error?: string;
}

export default function ChatWindow({
  messages,
  loading,
  error,
}: Props) {

    const bottomRef =
    useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages, loading]);
  return (
    <div className="flex flex-col flex-1 overflow-hidden">

      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        {messages.length === 0 && (
          <div className="text-center text-muted-foreground mt-20">
            Start a conversation with
            Smart Knowledge Bank.
          </div>
        )}

        {messages.map(
          (message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          )
        )}

        {loading && (
          <TypingIndicator />
        )}

        {error && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <div ref={bottomRef} />

      </div>

    </div>
  );
}