"use client"

import React from 'react';

interface HeatmapProps {
    sentenceScores: [string, number][];
}

export function Heatmap({ sentenceScores }: HeatmapProps) {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border text-sm leading-relaxed text-gray-800 max-h-[500px] overflow-y-auto">
            {sentenceScores.map(([sentence, score], index) => {
                let bgColor = "transparent";
                if (score > 0.6) bgColor = "#dcfce7"; // Green-100
                else if (score > 0.4) bgColor = "#ffedd5"; // Orange-100

                return (
                    <span key={index} style={{ backgroundColor: bgColor }} className="px-1 py-0.5 rounded mx-0.5">
                        {sentence}
                    </span>
                );
            })}
        </div>
    );
}
