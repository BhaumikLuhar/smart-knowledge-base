"use client";

import {

  Card,

} from "@/components/ui/card";

import {

  Badge,

} from "@/components/ui/badge";

import {

  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,

} from "@/components/ui/table";

import {

  AuditLog,

} from "@/types/audit";

interface AuditTableProps {

  logs: AuditLog[];

}

function getBadgeVariant(
  action: string
):
  | "default"
  | "secondary"
  | "destructive"
  | "outline" {

  switch (action) {

    case "login":
    case "logout":
      return "secondary";

    case "query":
      return "default";

    case "upload":
      return "outline";

    default:
      return "outline";

  }

}

export default function AuditTable({

  logs,

}: AuditTableProps) {

  return (

    <Card className="p-6">

      <div className="mb-4">

        <h2 className="text-xl font-semibold">

          Audit Logs

        </h2>

      </div>

      <Table>

        <TableHeader>

          <TableRow>

            <TableHead>User</TableHead>

            <TableHead>Action</TableHead>

            <TableHead>Resource</TableHead>

            <TableHead>Timestamp</TableHead>

          </TableRow>

        </TableHeader>

        <TableBody>

          {logs.length === 0 && (

            <TableRow>

              <TableCell
                colSpan={4}
                className="py-8 text-center text-muted-foreground"
              >

                No audit logs.

              </TableCell>

            </TableRow>

          )}

          {logs.map((log) => (

            <TableRow
              key={log.id}
            >

              <TableCell>

                {log.user_email ?? "-"}

              </TableCell>

              <TableCell>

                <Badge
                  variant={getBadgeVariant(
                    log.action
                  )}
                >

                  {log.action}

                </Badge>

              </TableCell>

              <TableCell>

                {log.resource_type ?? "-"}

              </TableCell>

              <TableCell>

                {new Date(
                  log.created_at
                ).toLocaleString()}

              </TableCell>

            </TableRow>

          ))}

        </TableBody>

      </Table>

    </Card>

  );

}