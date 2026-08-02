from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CompanyOut(BaseModel):
    id: int
    ticker: str
    name: str
    cik: str
    fiscal_year_end: str | None = None
    ir_url: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SourceDocumentOut(BaseModel):
    id: int
    company_id: int
    source_type: str
    title: str
    document_url: str | None = None
    local_path: str | None = None
    accession_number: str | None = None
    filing_type: str | None = None
    filed_at: date | None = None
    fetched_at: datetime | None = None
    parse_status: str
    metadata_json: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ManualMetricIn(BaseModel):
    quarter: str
    fiscal_year: int | None = None
    values: dict[str, Any]
    source_label: str = "Manual input"
    source_url: str | None = None
    notes: str | None = None


class RefreshResult(BaseModel):
    ticker: str
    filings_seen: int
    filings_cached: int
    metrics_updated: int
    message: str


class SignalResultOut(BaseModel):
    signal_key: str
    signal_name: str
    status: str
    summary: str
    triggered: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class DiagnosisOut(BaseModel):
    run_id: int | None = None
    ticker: str
    quarter: str | None = None
    overall_signal: str
    conclusion: str
    missing_metrics: list[str] = Field(default_factory=list)
    signals: list[SignalResultOut] = Field(default_factory=list)
    exit_signals: list[str] = Field(default_factory=list)
    scale_in_signals: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    report_path: str | None = None
