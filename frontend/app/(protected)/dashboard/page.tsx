"use client";

import { useEffect, useState } from "react";

import StatCard from "@/components/dashboard/stat-card";
import RecentQueryTable from "@/components/dashboard/recent-query-table";

import { getDashboardSummary } from "@/services/dashboard-service";

import { useAuth } from "@/contexts/AuthContext";

import {
  DashboardSummary,
} from "@/types/dashboard";

export default function DashboardPage() {

  const [summary, setSummary] =
    useState<DashboardSummary | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const { user } = useAuth();

  const isAdmin =
    user?.role === "admin";

  async function loadDashboard() {

    if (!isAdmin) {
      setLoading(false);
      return;
    }


    try {

      setLoading(true);

      setError("");

      const data =
        await getDashboardSummary();

      setSummary(data);

    } catch {

      setError(
        "Unable to load dashboard."
      );

    } finally {

      setLoading(false);

    }

  }

  useEffect(() => {

    if (isAdmin) {
      loadDashboard();
    } else {
      setLoading(false);
    }


  }, []);

  if (loading) {

    return (
      <div className="space-y-6">

        <h1 className="text-3xl font-bold">
          Dashboard
        </h1>

        <div className="text-muted-foreground">
          Loading dashboard...
        </div>

      </div>
    );

  }

  if (error) {

    return (
      <div className="space-y-6">

        <h1 className="text-3xl font-bold">
          Dashboard
        </h1>

        <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-700">
          {error}
        </div>

      </div>
    );

  }

  if (!isAdmin) {

    return (

      <div className="space-y-6">

        <h1 className="text-3xl font-bold">
          Dashboard
        </h1>

        <div className="rounded-lg border p-6 text-muted-foreground">
          Only administrators can access the dashboard.
        </div>

      </div>

    );

  }

  if (!summary) {

    return null;

  }

  return (

    <div className="space-y-8">

      <div>

        <h1 className="text-3xl font-bold">
          Dashboard
        </h1>

        <p className="text-muted-foreground">
          System overview and usage metrics.
        </p>

      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

        <StatCard
          title="Total Queries Today"
          value={
            summary.total_queries_today
          }
        />

        <StatCard
          title="Average Latency"
          value={`${summary.average_latency_ms} ms`}
        />

        <StatCard
          title="Active Users"
          value={
            summary.active_users
          }
        />

        <StatCard
          title="Documents Ready"
          value={
            summary.documents_ready
          }
        />

      </div>

      <RecentQueryTable
        queries={
          summary.recent_queries
        }
      />

    </div>

  );

}