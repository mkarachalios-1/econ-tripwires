export const fmt = (n?: number, unit?: string) =>
  n === undefined || n === null ? '—' :
  unit === '%' ? `${n.toFixed(2)}%` : n.toFixed(2);

export const statusColor = (s: string) =>
  s === 'severe' ? '#c0392b' : s === 'warn' ? '#f39c12' : s === 'ok' ? '#27ae60' : '#7f8c8d';
