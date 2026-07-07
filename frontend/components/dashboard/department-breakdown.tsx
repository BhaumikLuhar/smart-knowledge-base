"use client";

import { Card } from "@/components/ui/card";

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import {
    DepartmentBreakdown,
} from "@/types/dashboard";

interface Props {
    departments: DepartmentBreakdown[];
}

export default function DepartmentBreakdownTable({
    departments,
}: Props) {

    return (

        <Card className="p-6">

            <h2 className="text-xl font-semibold mb-4">
                Department Breakdown
            </h2>

            <Table>

                <TableHeader>

                    <TableRow>

                        <TableHead>
                            Department
                        </TableHead>

                        <TableHead>
                            Queries
                        </TableHead>

                        <TableHead>
                            Percentage
                        </TableHead>

                    </TableRow>

                </TableHeader>

                <TableBody>

                    {departments.map((item) => (

                        <TableRow key={item.department}>

                            <TableCell>
                                {item.department}
                            </TableCell>

                            <TableCell>
                                {item.query_count}
                            </TableCell>

                            <TableCell>
                                {item.percentage}%
                            </TableCell>

                        </TableRow>

                    ))}

                </TableBody>

            </Table>

        </Card>

    );

}