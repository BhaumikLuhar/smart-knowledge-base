import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import { Badge } from "@/components/ui/badge";

import { Document } from "@/types/document";

interface Props {
    documents: Document[];
}

function getStatusVariant(
    status: string
):
    | "default"
    | "secondary"
    | "destructive" {

    switch (status) {
        case "ready":
            return "default";

        case "failed":
            return "destructive";

        default:
            return "secondary";
    }
}

export default function DocumentTable({
    documents,
}: Props) {
    return (
        <div className="border rounded-lg">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>

                        <TableHead>
                            Department
                        </TableHead>

                        <TableHead>
                            Visibility
                        </TableHead>

                        <TableHead>Status</TableHead>

                        <TableHead>
                            Uploaded
                        </TableHead>

                        <TableHead>
                            Actions
                        </TableHead>
                    </TableRow>
                </TableHeader>

                <TableBody>
                    {documents.map((doc) => (
                        <TableRow key={doc.id}>
                            <TableCell>
                                {doc.name}
                            </TableCell>

                            <TableCell>
                                <Badge variant="secondary">
                                    {
                                        doc.department_display_name
                                    }
                                </Badge>
                            </TableCell>

                            <TableCell>
                                {doc.visibility}
                            </TableCell>

                            <TableCell>
                                <Badge
                                    variant={
                                        getStatusVariant(
                                            doc.status
                                        )
                                    }
                                >
                                    {doc.status}
                                </Badge>
                            </TableCell>

                            <TableCell>
                                {new Date(
                                    doc.created_at
                                ).toLocaleDateString()}
                            </TableCell>

                            <TableCell>
                                <button
                                    className="text-blue-600 hover:underline"
                                >
                                    View
                                </button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}