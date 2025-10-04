import React from 'react';
import Gauge from './Gauge';
import { fmt } from '../lib/format';
import type { Indicator } from '../data-schema';
import SeriesChart from './SeriesChart';

export default function IndicatorCard({ id, ind }: { id: string; ind: Indicator }) {
  const latest = ind.summary?.latest_value;
  const yoy = ind.summary?.yoy_pct;
  return (
    <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 16, marginBottom: 16, boxShadow: '0 1px 6px rgba(0,0,0,0.05)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent:'space-between', marginBottom: 8 }}>
        <div style={{ fontWeight: 700 }}>{ind.label}</div>
        <div><Gauge status={ind.status as any} /></div>
      </div>
      {ind.error ? (
        <div style={{ color: '#c0392b' }}>Error: {ind.error}</div>
      ) : (
        <>
          <div style={{ fontSize: 14, color: '#555', marginBottom: 8 }}>
            Latest ({ind.summary?.latest_date || '—'}): <b>{fmt(latest, ind.unit)}</b>
            {yoy !== undefined && yoy !== null ? <> • YoY: <b>{yoy.toFixed(2)}%</b></> : null}
          </div>
          <SeriesChart data={ind.series} unit={ind.unit} />
          <div style={{ fontSize: 12, color: '#888' }}>Source: {ind.source || '—'}</div>
        </>
      )}
    </div>
  );
}
