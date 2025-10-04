import React from 'react';
import { statusColor } from '../lib/format';

export default function Gauge({ status }:{status: 'ok'|'warn'|'severe'|'unknown'}) {
  const color = statusColor(status);
  return (
    <div style={{ width: 12, height: 12, borderRadius: 6, background: color, display: 'inline-block', marginRight: 8 }} title={status}/>
  );
}
