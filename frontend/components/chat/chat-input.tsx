"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  disabled?: boolean;
  onSend: (message: string) => Promise<void>;
}

export default function ChatInput({
  disabled = false,
  onSend,
}: ChatInputProps) {
  const [message, setMessage] =
    useState("");

  async function handleSend() {
    const trimmed = message.trim();

    if (!trimmed || disabled) {
      return;
    }

    await onSend(trimmed);

    setMessage("");
  }

  async function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      await handleSend();
    }
  }

  return (
    <div className="border-t p-4 space-y-3">

      <Textarea
        rows={3}
        value={message}
        disabled={disabled}
        placeholder="Ask a question..."
        onChange={(event) =>
          setMessage(
            event.target.value
          )
        }
        onKeyDown={handleKeyDown}
      />

      <div className="flex justify-end">

        <Button
          onClick={handleSend}
          disabled={
            disabled ||
            !message.trim()
          }
        >
          Send
        </Button>

      </div>

    </div>
  );
}