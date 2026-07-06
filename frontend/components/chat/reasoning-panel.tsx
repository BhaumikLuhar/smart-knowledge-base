"use client";

import { useState } from "react";

interface TraceStep {
  agent_name: string;
  input_summary: string;
  output_summary: string;
  latency: number;
}

interface Props {
  trace: TraceStep[];
}

export default function ReasoningPanel({
  trace,
}: Props) {
  const [open, setOpen] =
    useState(false);

  if (!trace.length) {
    return null;
  }

  return (
    <div className="mt-3">

      <button
        className="text-sm text-blue-600 hover:underline"
        onClick={() =>
          setOpen(!open)
        }
      >
        {open
          ? "Hide reasoning"
          : "Show reasoning"}
      </button>

      {open && (

        <div className="mt-3 space-y-4 rounded-lg border p-4">

          {trace.map((step) => (

            <div
              key={step.agent_name}
              className="rounded-md border p-3"
            >

              <div className="font-semibold capitalize">

                {step.agent_name}

              </div>

              <div className="mt-2 text-sm">

                <span className="font-medium">
                  Input:
                </span>

                <div className="text-muted-foreground break-words">

                  {step.input_summary}

                </div>

              </div>

              <div className="mt-2 text-sm">

                <span className="font-medium">
                  Output:
                </span>

                <div className="text-muted-foreground break-words">

                  {step.output_summary}

                </div>

              </div>

              <div className="mt-2 text-sm">

                <span className="font-medium">
                  Latency:
                </span>{" "}

                {step.latency.toFixed(2)} ms

              </div>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}