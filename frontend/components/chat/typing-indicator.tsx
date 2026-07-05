"use client";

import {
  useEffect,
  useState,
} from "react";

export default function TypingIndicator() {
  const [seconds, setSeconds] =
    useState(0);

  useEffect(() => {
    setSeconds(0);
    const timer = setInterval(() => {
      setSeconds(
        (previous) => previous + 1
      );
    }, 1000);

    return () =>
      clearInterval(timer);
  }, []);

  return (
    <div className="rounded-lg border bg-muted p-4 max-w-md">

      <div className="font-medium">
        Thinking... {seconds}s
      </div>

      {seconds >= 10 && (
        <div className="text-sm text-muted-foreground mt-1">
          Still working...
        </div>
      )}

    </div>
  );
}