import React from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts';
import type { Point } from '../data-schema';

export default function SeriesChart({ data, unit }: { data: Point[]; unit?: string }) {
  const rows = data.map(p => ({ name: p.d, value: p.v }));
  return (
    <div style={{ width: '100%', height: 240 }}>
      <ResponsiveContainer>
        <LineChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={false} />
          <YAxis width={60} />
          <Tooltip formatter={(v) => (unit === '%' ? `${(v as number).toFixed(2)}%` : (v as number).toFixed(3))} />
          <Line type="monotone" dataKey="value" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
