"use client";

import {
  Accordion,
  AccordionItem,
} from "@/components/ui/accordion";

import { Badge } from "@/components/ui/badge";

import { Citation } from "@/types/chat";

interface Props {
  citations: Citation[];
}

export default function CitationPanel({
  citations,
}: Props) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <Accordion>
      <AccordionItem
        defaultOpen
        title={`Citations (${citations.length})`}
      >
        <div className="space-y-3">

          {citations.map(
            (citation, index) => (
              <div
                key={index}
                className="rounded-lg border p-3"
              >
                <div className="flex items-center justify-between">

                  <div className="font-medium">
                    {citation.document_name}
                  </div>

                  {citation.department_id && (
                    <Badge
                      variant="outline"
                    >
                      {
                        citation.department_id
                      }
                    </Badge>
                  )}

                </div>

                <div className="text-sm text-muted-foreground mt-2">

                  Page{" "}
                  {citation.page_numbers.length
                    ? citation.page_numbers.join(
                        ", "
                      )
                    : "-"}

                </div>

                <p className="mt-3 text-sm">
                  {
                    citation.chunk_excerpt.length >
                    100
                      ? `${citation.chunk_excerpt.slice(
                          0,
                          100
                        )}...`
                      : citation.chunk_excerpt
                  }
                </p>

              </div>
            )
          )}

        </div>
      </AccordionItem>
    </Accordion>
  );
}