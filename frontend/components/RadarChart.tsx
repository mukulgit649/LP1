"use client"

import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface RadarChartProps {
    data: {
        subject: string;
        A: number;
        fullMark: number;
    }[];
}

export function SkillRadarChart({ data }: RadarChartProps) {
    return (
        <ResponsiveContainer width="100%" height={300}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                    name="Skills"
                    dataKey="A"
                    stroke="#2563eb"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                />
            </RadarChart>
        </ResponsiveContainer>
    );
}
