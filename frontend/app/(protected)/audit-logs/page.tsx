"use client";

import {

  useEffect,
  useState,

} from "react";

import LoadingState from "@/components/common/loading-state";
import ErrorCard from "@/components/common/error-card";
import EmptyState from "@/components/common/empty-state";

import AuditTable from "@/components/audit/audit-table";

import {

  getAuditLogs,

} from "@/services/audit-service";

import {

  AuditLog,

} from "@/types/audit";

import {

  useAuth,

} from "@/contexts/AuthContext";

export default function AuditLogsPage() {

  const { user } = useAuth();

  const isAdmin =
    user?.role === "admin";

  const [logs, setLogs] =
    useState<AuditLog[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadLogs() {

    try {

      setLoading(true);

      setError("");

      const response =
        await getAuditLogs();

      setLogs(
        response.items
      );

    } catch {

      setError(
        "Unable to load audit logs."
      );

    } finally {

      setLoading(false);

    }

  }

  useEffect(() => {

    if (isAdmin) {

      loadLogs();

    } else {

      setLoading(false);

    }

  }, []);

  if (!isAdmin) {

    return (

      <div className="space-y-4">

        <h1 className="text-3xl font-bold">

          Audit Logs

        </h1>

        <div className="rounded-lg border p-6 text-muted-foreground">

          Only administrators can access audit logs.

        </div>

      </div>

    );

  }

  if (loading) {

    return (

      <LoadingState
        title="Loading Audit Logs"
        description="Fetching recent system activity..."
      />

    );

  }

  if (error) {

    return (

      <ErrorCard
        message={error}
        onRetry={loadLogs}
      />

    );

  }

  if (logs.length === 0) {

    return (

      <EmptyState
        title="No audit logs"
        description="System activity will appear here."
      />

    );

  }

  return (

    <div className="space-y-8">

      <div>

        <h1 className="text-3xl font-bold">

          Audit Logs

        </h1>

        <p className="text-muted-foreground">

          View recent user activity across the system.

        </p>

      </div>

      <AuditTable
        logs={logs}
      />

    </div>

  );

}