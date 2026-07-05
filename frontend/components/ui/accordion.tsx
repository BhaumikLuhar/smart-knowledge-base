"use client";

import * as React from "react";

interface AccordionProps {
  children: React.ReactNode;
}

interface AccordionItemProps {
  title: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function Accordion({
  children,
}: AccordionProps) {
  return <div className="space-y-2">{children}</div>;
}

export function AccordionItem({
  title,
  children,
  defaultOpen = false,
}: AccordionItemProps) {
  const [open, setOpen] =
    React.useState(defaultOpen);

  return (
    <div className="border rounded-lg">
      <button
        type="button"
        className="w-full flex items-center justify-between p-3 text-left font-medium hover:bg-muted"
        onClick={() => setOpen(!open)}
      >
        <span>{title}</span>

        <span className="text-muted-foreground">
          {open ? "−" : "+"}
        </span>
      </button>

      {open && (
        <div className="border-t p-3">
          {children}
        </div>
      )}
    </div>
  );
}