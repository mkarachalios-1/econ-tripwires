export type Point = { d: string; v: number };
export type Indicator = {
  label: string;
  unit: string;
  status: 'ok'|'warn'|'severe'|'unknown';
  series: Point[];
  summary?: { latest_date?: string; latest_value?: number; yoy_pct?: number|null };
  source?: string;
  error?: string;
};
export type IndicatorsFile = {
  generated_utc: string;
  start_date: string;
  indicators: Record<string, Indicator>;
};
