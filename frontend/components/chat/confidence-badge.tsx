"use client";

import { Badge } from "@/components/ui/badge";

interface ConfidenceBadgeProps {
  level: "low" | "medium" | "high";
}

const styles = {
  high:
    "bg-green-100 text-green-700 border-green-300",

  medium:
    "bg-yellow-100 text-yellow-700 border-yellow-300",

  low:
    "bg-red-100 text-red-700 border-red-300",
};

export default function ConfidenceBadge({
  level,
}: ConfidenceBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={styles[level]}
    >
      {level.toUpperCase()} Confidence
    </Badge>
  );
}