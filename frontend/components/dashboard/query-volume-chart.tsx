"use client";

import {

    ResponsiveContainer,

    BarChart,

    Bar,

    CartesianGrid,

    Tooltip,

    XAxis,

    YAxis,

} from "recharts";

import { Card } from "@/components/ui/card";

import {

    HourlyQueryVolume,

} from "@/types/dashboard";

interface Props {

    data: HourlyQueryVolume[];

}

export default function QueryVolumeChart({

    data,

}: Props) {

    return (

        <Card className="p-6">

            <h2 className="text-xl font-semibold mb-4">

                Query Volume by Hour

            </h2>

            <ResponsiveContainer
                width="100%"
                height={300}
            >

                <BarChart
                    data={data}
                >

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="hour" />

                    <YAxis />

                    <Tooltip />

                    <Bar
                        dataKey="query_count"
                    />

                </BarChart>

            </ResponsiveContainer>

        </Card>

    );

}