"use client";

import { useState } from "react";

interface Props {
  trace: Record<string, unknown>[];
}

export default function ReasoningPanel({
  trace,
}: Props) {
  const [open, setOpen] = useState(false);

  if (!trace.length) {
    return null;
  }

  function value(
    agent: string,
    field: string
  ) {
    return trace.find(
      (step) => step.agent === agent
    )?.[field];
  }

  return (
    <div className="mt-3">

      <button
        className="text-sm text-blue-600 hover:underline"
        onClick={() => setOpen(!open)}
      >
        {open
          ? "Hide reasoning"
          : "Show reasoning"}
      </button>

      {open && (
        <div className="mt-3 rounded-lg border p-4 space-y-3 text-sm">

          <div>
            <strong>Planner</strong>
            <div>
              Strategy:{" "}
              {String(
                value(
                  "planner",
                  "strategy"
                ) ?? "-"
              )}
            </div>
          </div>

          <div>
            <strong>Research</strong>
            <div>
              Sources:{" "}
              {String(
                value(
                  "research",
                  "source_count"
                ) ?? "-"
              )}
            </div>
          </div>

          <div>
            <strong>Response</strong>
            <div>
              Tokens:{" "}
              {String(
                value(
                  "response",
                  "tokens_used"
                ) ?? "-"
              )}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}