"use client";

import {
  Badge,
} from "@/components/ui/badge";

import {
  Card,
} from "@/components/ui/card";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import {
  RecentQuery,
} from "@/types/dashboard";

interface RecentQueryTableProps {
  queries: RecentQuery[];
}

function getBadgeVariant(
  level: string
):
  | "default"
  | "secondary"
  | "destructive"
  | "outline" {

  switch (level) {

    case "high":
      return "default";

    case "medium":
      return "secondary";

    case "low":
      return "destructive";

    default:
      return "outline";
  }
}

export default function RecentQueryTable({
  queries,
}: RecentQueryTableProps) {

  return (

    <Card className="p-6">

      <div className="mb-4">

        <h2 className="text-xl font-semibold">
          Recent Queries
        </h2>

      </div>

      <Table>

        <TableHeader>

          <TableRow>

            <TableHead>
              User
            </TableHead>

            <TableHead>
              Query
            </TableHead>

            <TableHead>
              Confidence
            </TableHead>

            <TableHead>
              Time
            </TableHead>

          </TableRow>

        </TableHeader>

        <TableBody>

          {queries.length === 0 && (

            <TableRow>

              <TableCell
                colSpan={4}
                className="text-center py-8 text-muted-foreground"
              >
                No recent queries.
              </TableCell>

            </TableRow>

          )}

          {queries.map(
            (
              query,
              index
            ) => (

              <TableRow key={index}>

                <TableCell>

                  {query.user}

                </TableCell>

                <TableCell className="max-w-md truncate">

                  {query.query}

                </TableCell>

                <TableCell>

                  <Badge
                    variant={getBadgeVariant(
                      query.confidence
                    )}
                  >
                    {
                      query.confidence
                    }
                  </Badge>

                </TableCell>

                <TableCell>

                  {new Date(
                    query.timestamp
                  ).toLocaleString()}

                </TableCell>

              </TableRow>

            )
          )}

        </TableBody>

      </Table>

    </Card>

  );
}