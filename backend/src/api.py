from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.config import get_settings
from src.db import SessionLocal, get_session, initialize_runtime_schema
from src.models import Company, ModelRun, SourceDocument
from src.providers.sec_client import SECClient
from src.schemas import DiagnosisOut, ManualMetricIn, RefreshResult, SignalResultOut
from src.storage import (
    apply_manual_metrics,
    create_model_run,
    get_company,
    get_metric,
    latest_metric,
    latest_model_run,
    list_quarters,
    metric_to_dict,
    previous_metric_dicts,
    refresh_company_sources,
    seed_default_company,
)
from src.model.rules import evaluate_metrics


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        initialize_runtime_schema()
        with SessionLocal() as session:
            seed_default_company(session)
            session.commit()
    except Exception:
        pass
    yield


app = FastAPI(title="Kenepa Diagnostics API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5180", "http://127.0.0.1:5180"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _company_or_404(session: Session, ticker: str) -> Company:
    company = get_company(session, ticker)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {ticker.upper()} not found")
    return company


def _diagnosis_response(company: Company, run: ModelRun | None, diagnosis: Any | None = None) -> DiagnosisOut:
    if run and not diagnosis:
        signals = [
            SignalResultOut(
                signal_key=result.signal_key,
                signal_name=result.signal_name,
                status=result.status,
                summary=result.summary,
                triggered=result.triggered,
                details=result.details or {},
            )
            for result in run.signal_results
        ]
        return DiagnosisOut(
            run_id=run.id,
            ticker=company.ticker,
            quarter=run.quarter,
            overall_signal=run.overall_signal,
            conclusion=run.conclusion,
            missing_metrics=run.missing_metrics or [],
            signals=signals,
            created_at=run.created_at,
            report_path=run.report_path,
        )
    if diagnosis:
        return DiagnosisOut(
            run_id=run.id if run else None,
            ticker=company.ticker,
            quarter=run.quarter if run else None,
            overall_signal=diagnosis.overall_signal,
            conclusion=diagnosis.conclusion,
            missing_metrics=diagnosis.missing_metrics,
            signals=[SignalResultOut(**signal.__dict__) for signal in diagnosis.signals],
            exit_signals=diagnosis.exit_signals,
            scale_in_signals=diagnosis.scale_in_signals,
            created_at=run.created_at if run else None,
            report_path=run.report_path if run else None,
        )
    return DiagnosisOut(
        ticker=company.ticker,
        overall_signal="missing",
        conclusion="No model run exists yet. Refresh SEC data or enter manual metrics.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "kenepa-diagnostics-backend"}


@app.get("/api/companies")
def companies(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    seed_default_company(session)
    session.commit()
    rows = session.scalars(select(Company).order_by(Company.ticker)).all()
    return [
        {
            "id": row.id,
            "ticker": row.ticker,
            "name": row.name,
            "cik": row.cik,
            "fiscal_year_end": row.fiscal_year_end,
            "ir_url": row.ir_url,
            "metadata": row.metadata_json or {},
        }
        for row in rows
    ]


@app.get("/api/companies/{ticker}/quarters")
def quarters(ticker: str, session: Session = Depends(get_session)) -> list[str]:
    return list_quarters(session, _company_or_404(session, ticker))


@app.get("/api/companies/{ticker}/latest-diagnosis", response_model=DiagnosisOut)
def latest_diagnosis(ticker: str, session: Session = Depends(get_session)) -> DiagnosisOut:
    company = _company_or_404(session, ticker)
    run = latest_model_run(session, company)
    if run:
        metric = get_metric(session, company, run.quarter) if run.quarter else None
        if metric:
            diagnosis = evaluate_metrics(metric_to_dict(metric), previous_metric_dicts(session, metric))
            return _diagnosis_response(company, run, diagnosis)
        return _diagnosis_response(company, run)
    metric = latest_metric(session, company)
    if not metric:
        return _diagnosis_response(company, None)
    run, diagnosis = create_model_run(session, company, metric)
    session.commit()
    return _diagnosis_response(company, run, diagnosis)


@app.post("/api/companies/{ticker}/refresh", response_model=RefreshResult)
def refresh(
    ticker: str,
    limit: int = Query(default=20, ge=1, le=100),
    force: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> RefreshResult:
    company = _company_or_404(session, ticker)
    settings = get_settings()
    sec_client = SECClient(settings.sec_user_agent, settings.data_dir)
    try:
        result = refresh_company_sources(session, company, sec_client, limit=limit, force=force)
        metric = latest_metric(session, company)
        if metric:
            create_model_run(session, company, metric)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=502, detail=f"SEC refresh failed: {exc}") from exc
    return RefreshResult(ticker=company.ticker, message="SEC refresh completed", **result)


@app.get("/api/companies/{ticker}/metrics/{quarter}")
def metrics(ticker: str, quarter: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    company = _company_or_404(session, ticker)
    metric = get_metric(session, company, quarter)
    if not metric:
        return {"ticker": company.ticker, "quarter": quarter, "missing": True, "values": {}}
    return {"ticker": company.ticker, "missing": False, "values": metric_to_dict(metric)}


@app.post("/api/companies/{ticker}/manual-metrics", response_model=DiagnosisOut)
def manual_metrics(ticker: str, payload: ManualMetricIn, session: Session = Depends(get_session)) -> DiagnosisOut:
    company = _company_or_404(session, ticker)
    try:
        metric = apply_manual_metrics(session, company, payload)
        run, diagnosis = create_model_run(session, company, metric)
        session.commit()
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _diagnosis_response(company, run, diagnosis)


@app.get("/api/companies/{ticker}/sources")
def company_sources(ticker: str, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    company = _company_or_404(session, ticker)
    rows = session.scalars(
        select(SourceDocument).where(SourceDocument.company_id == company.id).order_by(desc(SourceDocument.fetched_at), desc(SourceDocument.id))
    ).all()
    return [
        {
            "id": row.id,
            "source_type": row.source_type,
            "title": row.title,
            "document_url": row.document_url,
            "local_path": row.local_path,
            "accession_number": row.accession_number,
            "filing_type": row.filing_type,
            "filed_at": row.filed_at.isoformat() if row.filed_at else None,
            "fetched_at": row.fetched_at.isoformat() if row.fetched_at else None,
            "parse_status": row.parse_status,
            "metadata": row.metadata_json or {},
        }
        for row in rows
    ]


@app.get("/api/reports")
def reports(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    rows = session.scalars(select(ModelRun).order_by(desc(ModelRun.created_at), desc(ModelRun.id))).all()
    return [
        {
            "run_id": row.id,
            "company_id": row.company_id,
            "quarter": row.quarter,
            "overall_signal": row.overall_signal,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "report_path": row.report_path,
        }
        for row in rows
    ]


@app.get("/api/reports/{run_id}")
def report(run_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    run = session.get(ModelRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Report not found")
    content = None
    if run.report_path and Path(run.report_path).exists():
        content = Path(run.report_path).read_text(encoding="utf-8")
    return {
        "run_id": run.id,
        "quarter": run.quarter,
        "overall_signal": run.overall_signal,
        "conclusion": run.conclusion,
        "report_path": run.report_path,
        "content": content,
    }


@app.get("/api/sources/{source_id}")
def source(source_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    row = session.get(SourceDocument, source_id)
    if not row:
        raise HTTPException(status_code=404, detail="Source document not found")
    return {
        "id": row.id,
        "company_id": row.company_id,
        "source_type": row.source_type,
        "title": row.title,
        "document_url": row.document_url,
        "local_path": row.local_path,
        "accession_number": row.accession_number,
        "filing_type": row.filing_type,
        "filed_at": row.filed_at.isoformat() if row.filed_at else None,
        "fetched_at": row.fetched_at.isoformat() if row.fetched_at else None,
        "parse_status": row.parse_status,
        "metadata": row.metadata_json or {},
    }
