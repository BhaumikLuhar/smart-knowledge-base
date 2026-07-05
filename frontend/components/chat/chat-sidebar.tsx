"use client";

import { Button } from "@/components/ui/button";

import { ChatSession } from "@/types/chat";

interface Props {
    sessions: ChatSession[];

    activeSessionId?: string;

    onSelect: (
        sessionId: string
    ) => void;

    onNewChat: () => void;

    disabled?: boolean;
}

export default function ChatSidebar({
    sessions,
    activeSessionId,
    onSelect,
    onNewChat,
    disabled = false,
}: Props) {
    return (
        <aside className="w-80 border-r flex flex-col">

            <div className="p-4 border-b">

                <Button
                    className="w-full"
                    onClick={onNewChat}
                    disabled={disabled}
                >
                    New Chat
                </Button>

            </div>

            <div className="overflow-y-auto flex-1">

                {sessions.map(
                    (session) => (
                        <button
                            key={session.id}
                            onClick={() =>
                                onSelect(
                                    session.id
                                )
                            }
                            disabled={disabled}
                            className={`w-full text-left p-4 border-b hover:bg-muted ${activeSessionId ===
                                session.id
                                ? "bg-muted"
                                : ""
                                }`}
                        >
                            <div className="font-medium truncate">
                                {session.last_message
                                    ? session.last_message.length > 50
                                        ? `${session.last_message.slice(0, 50)}...`
                                        : session.last_message
                                    : "New Conversation"}
                            </div>

                            <div className="text-xs text-muted-foreground mt-1">
                                {new Date(
                                    session.last_active
                                ).toLocaleString()}
                            </div>
                        </button>
                    )
                )}

                {sessions.length === 0 && (
                    <div className="p-6 text-center text-muted-foreground">
                        No conversations yet.
                    </div>
                )}

            </div>

        </aside>
    );
}