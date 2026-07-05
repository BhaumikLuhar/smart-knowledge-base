"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import { User } from "@/types/user";

interface UserTableProps {
    users: User[];

    loading: boolean;

    onEdit: (user: User) => void;
}

export default function UserTable({
    users,
    loading,
    onEdit,
}: UserTableProps) {
    return (
        <Table>

            <TableHeader>

                <TableRow>

                    <TableHead>Name</TableHead>

                    <TableHead>Email</TableHead>

                    <TableHead>Department</TableHead>

                    <TableHead>Role</TableHead>

                    <TableHead>Status</TableHead>

                    <TableHead>Last Login</TableHead>

                    <TableHead className="text-right">
                        Actions
                    </TableHead>

                </TableRow>

            </TableHeader>

            <TableBody>

                {loading ? (
                    <TableRow>
                        <TableCell
                            colSpan={7}
                            className="text-center text-muted-foreground py-10"
                        >
                            Loading users...
                        </TableCell>
                    </TableRow>
                ) : users.length === 0 ? (
                    <TableRow>
                        <TableCell
                            colSpan={7}
                            className="text-center text-muted-foreground py-10"
                        >
                            No users found.
                        </TableCell>
                    </TableRow>
                ) : (
                    users.map((user) => (
                        <TableRow key={user.id}>

                            <TableCell className="font-medium">
                                {user.full_name}
                            </TableCell>

                            <TableCell>
                                {user.email}
                            </TableCell>

                            <TableCell>

                                <Badge variant="outline">
                                    {user.department_name ??
                                        "None"}
                                </Badge>

                            </TableCell>

                            <TableCell>

                                <Badge
                                    variant={
                                        user.role === "admin"
                                            ? "default"
                                            : "secondary"
                                    }
                                >
                                    {user.role}
                                </Badge>

                            </TableCell>

                            <TableCell>

                                <Badge
                                    variant={
                                        user.is_active
                                            ? "default"
                                            : "destructive"
                                    }
                                >
                                    {user.is_active
                                        ? "Active"
                                        : "Inactive"}
                                </Badge>

                            </TableCell>

                            <TableCell>

                                {user.last_login
                                    ? new Date(
                                        user.last_login
                                    ).toLocaleString()
                                    : "-"}

                            </TableCell>

                            <TableCell className="text-right">

                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        onEdit(user)
                                    }
                                >
                                    Edit
                                </Button>

                            </TableCell>

                        </TableRow>
                    ))
                )}

            </TableBody>

        </Table>
    );
}