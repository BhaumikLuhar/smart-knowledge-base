"use client";

import CitationPanel from "./citation-panel";
import ConfidenceBadge from "./confidence-badge";
import ReasoningPanel from "./reasoning-panel";

import { ChatMessage } from "@/types/chat";

interface Props {
  message: ChatMessage;
}

export default function MessageBubble({
  message,
}: Props) {
  const isUser =
    message.role === "user";

  const metadata =
    (message.metadata ?? {}) as {
  confidence_level?: "low" | "medium" | "high";
  citations?: any[];
  trace?: Record<string, unknown>[];
};

  return (
    <div
      className={`flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`max-w-3xl rounded-lg p-4 ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        <p className="whitespace-pre-wrap">
          {message.content}
        </p>

        {!isUser && (
          <div className="space-y-4 mt-4">

            {metadata.confidence_level && (
              <ConfidenceBadge
                level={
                  metadata.confidence_level as
                    | "low"
                    | "medium"
                    | "high"
                }
              />
            )}

            <CitationPanel
              citations={
                (metadata.citations ??
                  []) as any[]
              }
            />

            <ReasoningPanel
              trace={
                (metadata.trace ??
                  []) as Record<
                  string,
                  unknown
                >[]
              }
            />

          </div>
        )}

      </div>
    </div>
  );
}