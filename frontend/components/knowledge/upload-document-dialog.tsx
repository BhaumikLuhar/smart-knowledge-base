"use client";

import { useState } from "react";

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";

import { Textarea } from "@/components/ui/textarea";

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

import {
    RadioGroup,
    RadioGroupItem,
} from "@/components/ui/radio-group";

import { Label } from "@/components/ui/label";

import { uploadDocument, getDocument } from "@/services/document-service";

import { Department } from "@/types/department";

interface Props {
    departments: Department[];
    onUploaded: () => void;
}

export default function UploadDocumentDialog({
    departments,
    onUploaded,
}: Props) {
    const [file, setFile] =
        useState<File | null>(null);

    const [departmentId, setDepartmentId] =
        useState("");

    const [visibility, setVisibility] =
        useState("department");

    const [description, setDescription] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    async function handleSubmit() {
        if (!file || !departmentId) {
            return;
        }

        try {
            setLoading(true);

            const formData = new FormData();

            formData.append(
                "file",
                file
            );

            formData.append(
                "department_id",
                departmentId
            );

            formData.append(
                "visibility",
                visibility
            );

            formData.append(
                "description",
                description
            );

            const document =
                await uploadDocument(
                    formData
                );

            onUploaded();

            const interval =
                setInterval(
                    async () => {
                        try {

                            const latest =
                                await getDocument(
                                    document.id
                                );

                            if (
                                latest.status === "ready" ||
                                latest.status === "failed"
                            ) {

                                clearInterval(
                                    interval
                                );

                                onUploaded();
                            }

                        } catch (error) {
                            console.error(
                                error
                            );
                        }
                    },
                    3000
                );

            setFile(null);

            setDepartmentId("");

            setVisibility(
                "department"
            );

            setDescription("");

        } finally {

            setLoading(false);
        }
    }

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button>
                    Upload Document
                </Button>
            </DialogTrigger>

            <DialogContent>
                <DialogHeader>
                    <DialogTitle>
                        Upload Document
                    </DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    <input
                        type="file"
                        onChange={(e) =>
                            setFile(
                                e.target.files?.[0] || null
                            )
                        }
                    />

                    <Select
                        onValueChange={
                            setDepartmentId
                        }
                    >
                        <SelectTrigger>
                            <SelectValue
                                placeholder="Department"
                            />
                        </SelectTrigger>

                        <SelectContent>
                            {departments.map((dept) => (
                                <SelectItem
                                    key={dept.id}
                                    value={dept.id}
                                >
                                    {dept.display_name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <RadioGroup
                        defaultValue="department"
                        onValueChange={
                            setVisibility
                        }
                    >
                        <div className="flex gap-2">
                            <RadioGroupItem
                                value="public"
                                id="public"
                            />

                            <Label htmlFor="public">
                                Public
                            </Label>
                        </div>

                        <div className="flex gap-2">
                            <RadioGroupItem
                                value="department"
                                id="department"
                            />

                            <Label htmlFor="department">
                                Department
                            </Label>
                        </div>

                        <div className="flex gap-2">
                            <RadioGroupItem
                                value="restricted"
                                id="restricted"
                            />

                            <Label htmlFor="restricted">
                                Restricted
                            </Label>
                        </div>
                    </RadioGroup>

                    <Textarea
                        placeholder="Description"
                        value={description}
                        onChange={(e) =>
                            setDescription(
                                e.target.value
                            )
                        }
                    />

                    <Button
                        className="w-full"
                        onClick={handleSubmit}
                        disabled={loading}
                    >
                        {loading
                            ? "Uploading..."
                            : "Upload"}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}