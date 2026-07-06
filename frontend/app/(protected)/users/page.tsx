"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/contexts/AuthContext";

import { Button } from "@/components/ui/button";

import UserTable from "@/components/users/user-table";
import UserDialog from "@/components/users/user-dialog";
import LoadingState from "@/components/common/loading-state";
import EmptyState from "@/components/common/empty-state";
import ErrorCard from "@/components/common/error-card";

import {
  createUser,
  getUsers,
  updateUser,
} from "@/services/user-service";

import { getDepartments } from "@/services/department-service";

import { User } from "@/types/user";
import { Department } from "@/types/department";

export default function UsersPage() {

  const { user } = useAuth();

  const [users, setUsers] =
    useState<User[]>([]);

  const [departments, setDepartments] =
    useState<Department[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [dialogOpen, setDialogOpen] =
    useState(false);

  const [editingUser, setEditingUser] =
    useState<User>();

  const [error, setError] =
    useState("");

  async function loadData() {

    setLoading(true);

    try {

      const [
        users,
        departments,
      ] = await Promise.all([
        getUsers(),
        getDepartments(),
      ]);

      setUsers(users);

      setDepartments(
        departments
      );

    } catch {
      setError(
        "Failed to load users."
      );
    }

    finally {

      setLoading(false);

    }

  }

  useEffect(() => {

    loadData();

  }, []);

  function handleAdd() {

    setEditingUser(undefined);

    setDialogOpen(true);

  }

  function handleEdit(
    user: User
  ) {

    setEditingUser(user);

    setDialogOpen(true);

  }

  async function handleSubmit(
    payload: {
      full_name: string;
      email: string;
      password: string;
      department_id: string | null;
      role: string;
      is_active: boolean;
    }
  ) {

    try {

      setLoading(true);

      if (editingUser) {

        await updateUser(
          editingUser.id,
          {
            role: payload.role,
            department_id:
              payload.department_id,
            is_active:
              payload.is_active,
          }
        );

      } else {

        await createUser(
          {
            full_name:
              payload.full_name,

            email:
              payload.email,

            password:
              payload.password,

            department_id:
              payload.department_id,

            role:
              payload.role,
          }
        );

      }

      setDialogOpen(false);

      setEditingUser(undefined);

      await loadData();

    } catch {

      setError(
        editingUser
          ? "Unable to update user."
          : "Unable to create user."
      );

    }
    finally {

      setLoading(false);

    }

  }

  //
  // Frontend role protection.
  //
  if (
    user?.role !== "admin"
  ) {

    return (
      <div className="space-y-4">

        <h1 className="text-3xl font-bold">
          Users
        </h1>

        <div className="rounded-lg border p-6">

          You do not have permission
          to access this page.

        </div>

      </div>
    );

  }

  if (loading && users.length === 0) {
    return (
      <LoadingState
        title="Loading Users"
        description="Fetching user accounts..."
      />
    );
  }

  if (error) {
    return (
      <div className="space-y-8">

        <div className="flex items-center justify-between">

          <div>

            <h1 className="text-3xl font-bold">
              Users
            </h1>

            <p className="text-muted-foreground">
              Manage system users.
            </p>

          </div>

          <Button
            onClick={handleAdd}
            disabled
          >
            Add User
          </Button>

        </div>

        <ErrorCard
          message={error}
          onRetry={loadData}
        />

      </div>
    );
  }

  return (
    <div className="space-y-8">

      <div className="flex items-center justify-between">

        <div>

          <h1 className="text-3xl font-bold">
            Users
          </h1>

          <p className="text-muted-foreground">

            Manage system users.

          </p>

        </div>

        <Button
          disabled={loading}
          onClick={handleAdd}
        >
          Add User
        </Button>

      </div>

      {users.length === 0 ? (
        <EmptyState
          title="No users found"
          description="Create your first user to get started."
        />
      ) : (
        <UserTable
          users={users}
          loading={loading}
          onEdit={handleEdit}
        />
      )}

      <UserDialog
        open={dialogOpen}
        user={editingUser}
        departments={departments}
        loading={loading}
        onClose={() => {

          setDialogOpen(false);

          setEditingUser(undefined);

        }}
        onSubmit={handleSubmit}
      />

    </div>
  );

}