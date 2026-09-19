export type Company = {
  id: number
  ticker: string
  name: string
  cik: string
  fiscal_year_end?: string
  ir_url?: string
  metadata?: Record<string, unknown>
}

export type SignalResult = {
  signal_key: string
  signal_name: string
  status: string
  summary: string
  triggered: boolean
  details: Record<string, unknown>
}

export type Diagnosis = {
  run_id: number | null
  ticker: string
  quarter: string | null
  overall_signal: string
  conclusion: string
  missing_metrics: string[]
  signals: SignalResult[]
  exit_signals: string[]
  scale_in_signals: string[]
  created_at?: string
  report_path?: string
}

export type MetricsResponse = {
  ticker: string
  quarter: string
  missing: boolean
  values: Record<string, unknown>
}

export type SourceDocument = {
  id: number
  source_type: string
  title: string
  document_url?: string
  local_path?: string
  accession_number?: string
  filing_type?: string
  filed_at?: string
  fetched_at?: string
  parse_status: string
  metadata: Record<string, unknown>
}

export type ReportSummary = {
  run_id: number
  quarter: string | null
  overall_signal: string
  created_at?: string
  report_path?: string
}

const configuredApiBase = import.meta.env.VITE_API_BASE_URL?.trim()
const API_BASE = configuredApiBase && !configuredApiBase.includes('$')
  ? configuredApiBase.replace(/\/+$/, '')
  : import.meta.env.DEV
    ? 'http://localhost:8000'
    : ''

function apiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  if (!API_BASE) return normalizedPath
  if (API_BASE.endsWith('/api') && normalizedPath.startsWith('/api/')) {
    return `${API_BASE}${normalizedPath.slice('/api'.length)}`
  }
  return `${API_BASE}${normalizedPath}`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!response.ok) {
    let message = response.statusText
    try {
      const body = await response.json()
      message = body.detail ?? message
    } catch {
      message = await response.text()
    }
    throw new Error(message)
  }
  return response.json() as Promise<T>
}

export const api = {
  companies: () => request<Company[]>('/api/companies'),
  quarters: (ticker: string) => request<string[]>(`/api/companies/${ticker}/quarters`),
  latestDiagnosis: (ticker: string) => request<Diagnosis>(`/api/companies/${ticker}/latest-diagnosis`),
  refresh: (ticker: string) => request(`/api/companies/${ticker}/refresh`, { method: 'POST' }),
  metrics: (ticker: string, quarter: string) => request<MetricsResponse>(`/api/companies/${ticker}/metrics/${encodeURIComponent(quarter)}`),
  manualMetrics: (ticker: string, payload: Record<string, unknown>) => request<Diagnosis>(`/api/companies/${ticker}/manual-metrics`, { method: 'POST', body: JSON.stringify(payload) }),
  sources: (ticker: string) => request<SourceDocument[]>(`/api/companies/${ticker}/sources`),
  reports: () => request<ReportSummary[]>('/api/reports'),
  report: (runId: number) => request<{ content: string | null; report_path?: string }>(`/api/reports/${runId}`),
}
