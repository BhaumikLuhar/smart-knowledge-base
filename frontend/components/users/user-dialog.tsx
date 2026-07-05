"use client";

import { useEffect, useState } from "react";

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

import { Department } from "@/types/department";
import { User } from "@/types/user";

interface UserDialogProps {
    open: boolean;

    user?: User;

    departments: Department[];

    loading?: boolean;

    onClose: () => void;

    onSubmit: (payload: {
        full_name: string;
        email: string;
        password: string;
        department_id: string | null;
        role: string;
        is_active: boolean;
    }) => Promise<void>;
}

export default function UserDialog({
    open,
    user,
    departments,
    loading = false,
    onClose,
    onSubmit,
}: UserDialogProps) {
    const isEdit = !!user;

    const [fullName, setFullName] =
        useState("");

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [departmentId, setDepartmentId] =
        useState("");

    const [role, setRole] =
        useState("employee");

    const [status, setStatus] =
        useState("active");

    useEffect(() => {
        if (user) {
            setFullName(user.full_name);

            setEmail(user.email);

            setPassword("");

            setDepartmentId(
                user.department_id ?? ""
            );

            setRole(user.role);

            setStatus(
                user.is_active
                    ? "active"
                    : "inactive"
            );
        } else {
            setFullName("");

            setEmail("");

            setPassword("");

            setDepartmentId("");

            setRole("employee");

            setStatus("active");
        }
    }, [user, open]);

    async function handleSubmit() {
        if (!fullName.trim()) {
            return;
        }

        if (!email.trim()) {
            return;
        }

        if (!isEdit && !password.trim()) {
            return;
        }

        if (
            role !== "admin" &&
            !departmentId
        ) {
            return;
        }
        await onSubmit({
            full_name: fullName,
            email,
            password,
            department_id:
                role === "admin"
                    ? null
                    : departmentId || null,
            role,
            is_active:
                status === "active",
        });
    }

    return (
        <Dialog
            open={open}
            onOpenChange={(value) => {
                if (!value) {
                    onClose();
                }
            }}
        >
            <DialogContent className="sm:max-w-lg">

                <DialogHeader>

                    <DialogTitle>
                        {isEdit
                            ? "Edit User"
                            : "Add User"}
                    </DialogTitle>

                    <DialogDescription>
                        {isEdit
                            ? "Update user information."
                            : "Create a new user."}
                    </DialogDescription>

                </DialogHeader>

                <div className="space-y-4">

                    <div>

                        <Label>
                            Full Name
                        </Label>

                        <Input
                            value={fullName}
                            onChange={(event) =>
                                setFullName(
                                    event.target.value
                                )
                            }
                        />

                    </div>

                    <div>

                        <Label>
                            Email
                        </Label>

                        <Input
                            type="email"
                            disabled={isEdit}
                            value={email}
                            onChange={(event) =>
                                setEmail(
                                    event.target.value
                                )
                            }
                        />

                    </div>

                    {!isEdit && (
                        <div>

                            <Label>
                                Password
                            </Label>

                            <Input
                                type="password"
                                value={password}
                                onChange={(event) =>
                                    setPassword(
                                        event.target.value
                                    )
                                }
                            />

                        </div>
                    )}

                    <div>

                        <Label>
                            Department
                        </Label>

                        <Select
                            value={
                                role === "admin"
                                    ? "none"
                                    : departmentId
                            }
                            onValueChange={(value) => {
                                if (value === "none") {
                                    setDepartmentId("");
                                } else {
                                    setDepartmentId(value);
                                }
                            }}
                            disabled={role === "admin"}
                        >
                            <SelectTrigger className="w-full">

                                <SelectValue placeholder="Select Department" />

                            </SelectTrigger>

                            <SelectContent>

                                <SelectItem value="none">
                                    No Department
                                </SelectItem>

                                {departments.map((department) => (
                                    <SelectItem
                                        key={department.id}
                                        value={department.id}
                                    >
                                        {department.display_name}
                                    </SelectItem>
                                ))}

                            </SelectContent>

                        </Select>

                    </div>

                    <div>

                        <Label>
                            Role
                        </Label>

                        <Select
                            value={role}
                            onValueChange={setRole}
                        >
                            <SelectTrigger className="w-full">

                                <SelectValue />

                            </SelectTrigger>

                            <SelectContent>

                                <SelectItem value="employee">
                                    Employee
                                </SelectItem>

                                <SelectItem value="manager">
                                    Manager
                                </SelectItem>

                                <SelectItem value="admin">
                                    Admin
                                </SelectItem>

                            </SelectContent>

                        </Select>

                    </div>

                    <div>

                        <Label>
                            Status
                        </Label>

                        <Select
                            value={status}
                            onValueChange={
                                setStatus
                            }
                        >
                            <SelectTrigger className="w-full">

                                <SelectValue />

                            </SelectTrigger>

                            <SelectContent>

                                <SelectItem value="active">
                                    Active
                                </SelectItem>

                                <SelectItem value="inactive">
                                    Inactive
                                </SelectItem>

                            </SelectContent>

                        </Select>

                    </div>

                </div>

                <DialogFooter>

                    <Button
                        variant="outline"
                        onClick={onClose}
                    >
                        Cancel
                    </Button>

                    <Button
                        disabled={loading}
                        onClick={handleSubmit}
                    >
                        {loading
                            ? "Saving..."
                            : isEdit
                                ? "Update User"
                                : "Create User"}
                    </Button>

                </DialogFooter>

            </DialogContent>

        </Dialog>
    );
}