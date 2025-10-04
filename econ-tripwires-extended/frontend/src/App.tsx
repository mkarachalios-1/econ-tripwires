import React, { useEffect, useState } from 'react';
import type { IndicatorsFile } from './data-schema';
import IndicatorCard from './components/IndicatorCard';

export default function App() {
  const [data, setData] = useState<IndicatorsFile | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const base = (import.meta as any).env.BASE_URL || '/';

  useEffect(() => {
    fetch(base + 'public-data/indicators.json?cachebust=' + Date.now())
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(setData)
      .catch(e => setErr(String(e)));
  }, []);

  if (err) return <div style={{padding:24}}>Failed to load data: {err}</div>;
  if (!data) return <div style={{padding:24}}>Loading…</div>;

  const entries = Object.entries(data.indicators);

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: 24 }}>
      <h1 style={{ marginBottom: 4 }}>Economic Tripwires</h1>
      <div style={{ color:'#666', marginBottom: 16 }}>
        Updated: {new Date(data.generated_utc).toLocaleString()} • Window: last 10 years
      </div>
      {entries.length === 0 && (
        <div style={{marginBottom:16}}>No indicators yet. Run the data workflow to populate series.</div>
      )}
      {entries.map(([id, ind]) => (
        <IndicatorCard key={id} id={id} ind={ind as any} />
      ))}
      <footer style={{ fontSize:12, color:'#888', marginTop: 24 }}>
        This is a monitoring dashboard, not a forecast. Thresholds are configurable in <code>data-pipeline/indicators.yaml</code>.
      </footer>
    </div>
  );
}
