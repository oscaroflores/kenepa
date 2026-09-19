from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.config import get_settings
from src.model.rules import Diagnosis, evaluate_metrics
from src.models import Company, Filing, ModelRun, ModelSignalResult, QuarterlyMetric, SourceDocument
from src.parsers.sec_facts import parse_companyfacts_to_metrics
from src.providers.sec_client import SECClient
from src.report import write_markdown_report


METRIC_FIELDS = [
    "share_price_used",
    "market_cap",
    "enterprise_value",
    "cash_and_equivalents",
    "subscription_revenue_growth",
    "current_rpo_growth",
    "current_rpo_growth_constant_currency",
    "renewal_rate",
    "gaap_net_income",
    "non_gaap_operating_margin",
    "free_cash_flow",
    "free_cash_flow_margin",
    "stock_based_compensation",
    "diluted_share_count",
    "buyback_authorization_remaining",
    "ai_acv_run_rate",
    "ai_acv_target",
    "creator_other_share",
    "customers_over_5m_acv",
    "named_competitive_wins",
    "named_displacements",
    "fy_growth_guidance",
    "fy_operating_margin_guidance",
    "fy27_growth_guidance",
    "discretionary_insider_selling_depressed",
]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _profile_path() -> Path:
    settings = get_settings()
    profile_path = settings.companies_dir / "servicenow" / "profile.yaml"
    if profile_path.exists():
        return profile_path
    return Path(__file__).resolve().parents[2] / "companies" / "servicenow" / "profile.yaml"


def load_company_profile() -> dict[str, Any]:
    with _profile_path().open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def seed_default_company(session: Session) -> Company:
    profile = load_company_profile()
    ticker = profile["ticker"].upper()
    company = session.scalar(select(Company).where(Company.ticker == ticker))
    if company:
        return company
    company = Company(
        ticker=ticker,
        name=profile["name"],
        cik=str(profile["cik"]),
        fiscal_year_end=str(profile.get("fiscal_year_end") or ""),
        ir_url=profile.get("ir_url"),
        metadata_json=profile,
    )
    session.add(company)
    session.flush()
    return company


def get_company(session: Session, ticker: str) -> Company | None:
    return session.scalar(select(Company).where(Company.ticker == ticker.upper()))


def upsert_source_document(
    session: Session,
    company: Company,
    *,
    source_type: str,
    title: str,
    document_url: str | None = None,
    local_path: str | None = None,
    accession_number: str | None = None,
    filing_type: str | None = None,
    filed_at: date | None = None,
    parse_status: str = "cached",
    metadata: dict[str, Any] | None = None,
) -> SourceDocument:
    query = select(SourceDocument).where(SourceDocument.company_id == company.id, SourceDocument.source_type == source_type)
    if accession_number:
        query = query.where(SourceDocument.accession_number == accession_number)
    elif document_url:
        query = query.where(SourceDocument.document_url == document_url)
    else:
        query = query.where(SourceDocument.title == title)
    doc = session.scalar(query)
    if not doc:
        doc = SourceDocument(company_id=company.id, source_type=source_type, title=title, metadata_json={})
        session.add(doc)
    doc.title = title
    doc.document_url = document_url
    doc.local_path = local_path
    doc.accession_number = accession_number
    doc.filing_type = filing_type
    doc.filed_at = filed_at
    doc.parse_status = parse_status
    doc.metadata_json = metadata or {}
    session.flush()
    return doc


def upsert_filing(
    session: Session,
    company: Company,
    *,
    source_document: SourceDocument | None,
    accession_number: str,
    form_type: str,
    filing_date: date | None,
    report_date: date | None,
    primary_document: str | None,
    sec_url: str | None,
    local_path: str | None,
    parse_status: str,
    metadata: dict[str, Any] | None = None,
) -> Filing:
    filing = session.scalar(
        select(Filing).where(Filing.company_id == company.id, Filing.accession_number == accession_number)
    )
    if not filing:
        filing = Filing(company_id=company.id, accession_number=accession_number, form_type=form_type, metadata_json={})
        session.add(filing)
    filing.source_document_id = source_document.id if source_document else None
    filing.form_type = form_type
    filing.filing_date = filing_date
    filing.report_date = report_date
    filing.primary_document = primary_document
    filing.sec_url = sec_url
    filing.local_path = local_path
    filing.parse_status = parse_status
    filing.metadata_json = metadata or {}
    session.flush()
    return filing


def ensure_metric_record(session: Session, company: Company, quarter: str, fiscal_year: int | None = None) -> QuarterlyMetric:
    metric = session.scalar(select(QuarterlyMetric).where(QuarterlyMetric.company_id == company.id, QuarterlyMetric.quarter == quarter))
    if not metric:
        metric = QuarterlyMetric(
            company_id=company.id,
            quarter=quarter,
            fiscal_year=fiscal_year,
            metric_sources={},
            manual_fields=[],
            missing_fields=[],
        )
        session.add(metric)
    if fiscal_year and not metric.fiscal_year:
        metric.fiscal_year = fiscal_year
    session.flush()
    return metric


def update_missing_fields(metric: QuarterlyMetric) -> None:
    metric.missing_fields = [field for field in METRIC_FIELDS if getattr(metric, field) is None]


def apply_parsed_metrics(metric: QuarterlyMetric, values: dict[str, Any], source_document: SourceDocument, details: dict[str, Any]) -> int:
    changed = 0
    manual_fields = set(metric.manual_fields or [])
    metric_sources = dict(metric.metric_sources or {})
    for field, value in values.items():
        if field not in METRIC_FIELDS or field in manual_fields:
            continue
        setattr(metric, field, value)
        metric_sources[field] = {
            "source_document_id": source_document.id,
            "mode": "parsed",
            "source_type": source_document.source_type,
            "detail": details.get(field, {}),
        }
        changed += 1
    metric.metric_sources = metric_sources
    update_missing_fields(metric)
    return changed


def apply_manual_metrics(session: Session, company: Company, payload: Any) -> QuarterlyMetric:
    metric = ensure_metric_record(session, company, payload.quarter, payload.fiscal_year)
    unknown = sorted(set(payload.values) - set(METRIC_FIELDS))
    if unknown:
        raise ValueError(f"Unknown metric fields: {', '.join(unknown)}")
    source = upsert_source_document(
        session,
        company,
        source_type="manual",
        title=payload.source_label,
        document_url=payload.source_url,
        parse_status="manual",
        metadata={"quarter": payload.quarter, "notes": payload.notes},
    )
    manual_fields = set(metric.manual_fields or [])
    metric_sources = dict(metric.metric_sources or {})
    for field, value in payload.values.items():
        setattr(metric, field, value)
        manual_fields.add(field)
        metric_sources[field] = {
            "source_document_id": source.id,
            "mode": "manual",
            "source_type": "manual",
            "label": payload.source_label,
            "url": payload.source_url,
            "notes": payload.notes,
        }
    metric.manual_fields = sorted(manual_fields)
    metric.metric_sources = metric_sources
    update_missing_fields(metric)
    session.flush()
    return metric


def metric_to_dict(metric: QuarterlyMetric | None) -> dict[str, Any]:
    if not metric:
        return {}
    data = {field: getattr(metric, field) for field in METRIC_FIELDS}
    data.update(
        {
            "id": metric.id,
            "company_id": metric.company_id,
            "quarter": metric.quarter,
            "fiscal_year": metric.fiscal_year,
            "metric_sources": metric.metric_sources or {},
            "manual_fields": metric.manual_fields or [],
            "missing_fields": metric.missing_fields or [],
            "updated_at": metric.updated_at.isoformat() if metric.updated_at else None,
        }
    )
    return data


def list_quarters(session: Session, company: Company) -> list[str]:
    rows = session.scalars(
        select(QuarterlyMetric.quarter).where(QuarterlyMetric.company_id == company.id).order_by(desc(QuarterlyMetric.id))
    ).all()
    return list(rows)


def get_metric(session: Session, company: Company, quarter: str) -> QuarterlyMetric | None:
    return session.scalar(select(QuarterlyMetric).where(QuarterlyMetric.company_id == company.id, QuarterlyMetric.quarter == quarter))


def latest_metric(session: Session, company: Company) -> QuarterlyMetric | None:
    return session.scalar(select(QuarterlyMetric).where(QuarterlyMetric.company_id == company.id).order_by(desc(QuarterlyMetric.id)).limit(1))


def previous_metric_dicts(session: Session, metric: QuarterlyMetric, limit: int = 4) -> list[dict[str, Any]]:
    rows = session.scalars(
        select(QuarterlyMetric)
        .where(QuarterlyMetric.company_id == metric.company_id, QuarterlyMetric.id < metric.id)
        .order_by(desc(QuarterlyMetric.id))
        .limit(limit)
    ).all()
    return [metric_to_dict(row) for row in rows]


def refresh_company_sources(session: Session, company: Company, sec_client: SECClient, limit: int = 20, force: bool = False) -> dict[str, Any]:
    submissions, submissions_path = sec_client.fetch_submissions(company.cik, force=force)
    upsert_source_document(
        session,
        company,
        source_type="sec_submissions",
        title=f"SEC submissions CIK{sec_client.cik10(company.cik)}",
        document_url=sec_client.submissions_url(company.cik),
        local_path=str(submissions_path),
        parse_status="cached",
        metadata={"description": "SEC submissions API cache"},
    )

    companyfacts, facts_path = sec_client.fetch_companyfacts(company.cik, force=force)
    facts_doc = upsert_source_document(
        session,
        company,
        source_type="sec_companyfacts",
        title=f"SEC companyfacts CIK{sec_client.cik10(company.cik)}",
        document_url=sec_client.companyfacts_url(company.cik),
        local_path=str(facts_path),
        parse_status="best_effort_parsed",
        metadata={"description": "SEC companyfacts API cache"},
    )

    recent = submissions.get("filings", {}).get("recent", {})
    accessions = recent.get("accessionNumber", [])
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    primary_documents = recent.get("primaryDocument", [])
    filings_cached = 0

    for index, accession in enumerate(accessions[:limit]):
        form_type = forms[index] if index < len(forms) else None
        if form_type not in {"10-K", "10-Q", "8-K", "4"}:
            continue
        primary_document = primary_documents[index] if index < len(primary_documents) else None
        filing_date = _parse_date(filing_dates[index] if index < len(filing_dates) else None)
        report_date = _parse_date(report_dates[index] if index < len(report_dates) else None)
        local_path = None
        sec_url = None
        parse_status = "metadata_only"
        metadata: dict[str, Any] = {}
        if primary_document:
            sec_url = sec_client.filing_document_url(company.cik, accession, primary_document)
            try:
                path, sec_url = sec_client.download_filing_document(company.ticker, company.cik, accession, primary_document, force=force)
                local_path = str(path)
                parse_status = "cached"
            except Exception as exc:  # noqa: BLE001 - keep refresh resilient and visible in source metadata.
                metadata["download_error"] = str(exc)
                parse_status = "download_failed"
        source = upsert_source_document(
            session,
            company,
            source_type="sec_filing",
            title=f"{company.ticker} {form_type} {filing_date or accession}",
            document_url=sec_url,
            local_path=local_path,
            accession_number=accession,
            filing_type=form_type,
            filed_at=filing_date,
            parse_status=parse_status,
            metadata=metadata,
        )
        upsert_filing(
            session,
            company,
            source_document=source,
            accession_number=accession,
            form_type=form_type,
            filing_date=filing_date,
            report_date=report_date,
            primary_document=primary_document,
            sec_url=sec_url,
            local_path=local_path,
            parse_status=parse_status,
            metadata=metadata,
        )
        filings_cached += 1

    metrics_updated = 0
    parsed = parse_companyfacts_to_metrics(companyfacts)
    if parsed:
        metric = ensure_metric_record(session, company, parsed["quarter"], parsed.get("fiscal_year"))
        metrics_updated = apply_parsed_metrics(metric, parsed["values"], facts_doc, parsed.get("fact_details", {}))

    session.flush()
    return {"filings_seen": min(len(accessions), limit), "filings_cached": filings_cached, "metrics_updated": metrics_updated}


def create_model_run(session: Session, company: Company, metric: QuarterlyMetric | None) -> tuple[ModelRun, Diagnosis]:
    metrics = metric_to_dict(metric)
    history = previous_metric_dicts(session, metric) if metric else []
    diagnosis = evaluate_metrics(metrics, history)
    run = ModelRun(
        company_id=company.id,
        quarter=metric.quarter if metric else None,
        status="completed",
        overall_signal=diagnosis.overall_signal,
        conclusion=diagnosis.conclusion,
        missing_metrics=diagnosis.missing_metrics,
    )
    session.add(run)
    session.flush()
    for signal in diagnosis.signals:
        session.add(
            ModelSignalResult(
                run_id=run.id,
                signal_key=signal.signal_key,
                signal_name=signal.signal_name,
                status=signal.status,
                summary=signal.summary,
                triggered=signal.triggered,
                details=signal.details,
            )
        )
    report_path = write_markdown_report(get_settings().reports_dir, run.id, company.ticker, run.quarter, metrics, diagnosis)
    run.report_path = str(report_path)
    session.flush()
    return run, diagnosis


def latest_model_run(session: Session, company: Company) -> ModelRun | None:
    return session.scalar(select(ModelRun).where(ModelRun.company_id == company.id).order_by(desc(ModelRun.created_at), desc(ModelRun.id)).limit(1))
