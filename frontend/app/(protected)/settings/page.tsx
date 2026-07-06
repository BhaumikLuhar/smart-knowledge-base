"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import LoadingState from "@/components/common/loading-state";
import ErrorCard from "@/components/common/error-card";
import {
  getSystemConfig,
} from "@/services/dashboard-service";

import {
  SystemConfig,
} from "@/types/dashboard";

import {
  getCurrentUser,
  changePassword,
} from "@/services/auth-service";

import {
  UserProfile,
} from "@/types/auth";

export default function SettingsPage() {
  const [profile, setProfile] =
    useState<UserProfile | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [currentPassword, setCurrentPassword] =
    useState("");

  const [newPassword, setNewPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [config, setConfig] =
    useState<SystemConfig | null>(
      null
    );

  async function loadProfile() {
    try {
      setLoading(true);

      const user =
        await getCurrentUser();

      setProfile(user);

      if (user.role === "admin") {

        const systemConfig =
          await getSystemConfig();

        setConfig(systemConfig);

      }
    } catch {
      setError(
        "Unable to load profile."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  async function handlePasswordChange() {
    setError("");
    setSuccess("");

    if (
      newPassword !== confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );

      return;
    }

    try {
      await changePassword({
        current_password:
          currentPassword,

        new_password:
          newPassword,

        confirm_password:
          confirmPassword,
      });

      setSuccess(
        "Password updated successfully."
      );

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch {
      setError(
        "Unable to update password."
      );
    }
  }

  if (loading) {
    return (
      <LoadingState
        title="Loading Settings"
        description="Fetching your profile and system configuration..."
      />
    );
  }

  if (error && !profile) {
    return (
      <ErrorCard
        message={error}
        onRetry={loadProfile}
      />
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">
        Settings
      </h1>

      <Card className="p-6 space-y-4">
        <h2 className="text-xl font-semibold">
          Profile
        </h2>

        <Input
          value={profile?.full_name ?? ""}
          readOnly
        />

        <Input
          value={profile?.email ?? ""}
          readOnly
        />

        <Input
          value={
            profile?.department_name ??
            "No Department"
          }
          readOnly
        />

        <Input
          value={profile?.role ?? ""}
          readOnly
        />
      </Card>

      <Card className="p-6 space-y-4">
        <h2 className="text-xl font-semibold">
          Change Password
        </h2>

        <Input
          type="password"
          placeholder="Current Password"
          value={currentPassword}
          onChange={(e) =>
            setCurrentPassword(
              e.target.value
            )
          }
        />

        <Input
          type="password"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) =>
            setNewPassword(
              e.target.value
            )
          }
        />

        <Input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(
              e.target.value
            )
          }
        />

        <Button
          onClick={
            handlePasswordChange
          }
        >
          Update Password
        </Button>

        {error && (
          <p className="text-red-600">
            {error}
          </p>
        )}

        {success && (
          <p className="text-green-600">
            {success}
          </p>
        )}
      </Card>

      {profile?.role === "admin" && config && (

        <Card className="p-6 space-y-3">

          <h2 className="text-xl font-semibold">

            System Configuration

          </h2>

          <div className="grid gap-3 md:grid-cols-2">

            <div>

              <p className="text-sm text-muted-foreground">
                Chunk Size
              </p>

              <Input
                readOnly
                value={config.chunk_size}
              />

            </div>

            <div>

              <p className="text-sm text-muted-foreground">
                Chunk Overlap
              </p>

              <Input
                readOnly
                value={config.chunk_overlap}
              />

            </div>

            <div>

              <p className="text-sm text-muted-foreground">
                Candidate Top K
              </p>

              <Input
                readOnly
                value={config.candidate_top_k}
              />

            </div>

            <div>

              <p className="text-sm text-muted-foreground">
                Final Top K
              </p>

              <Input
                readOnly
                value={config.final_top_k}
              />

            </div>

            <div>

              <p className="text-sm text-muted-foreground">
                Max Sessions
              </p>

              <Input
                readOnly
                value={config.max_sessions}
              />

            </div>

          </div>

        </Card>

      )}
    </div>
  );
}