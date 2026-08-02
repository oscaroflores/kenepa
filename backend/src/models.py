from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    cik: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    fiscal_year_end: Mapped[str | None] = mapped_column(String(8), nullable=True)
    ir_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    filings: Mapped[list["Filing"]] = relationship(back_populates="company")
    source_documents: Mapped[list["SourceDocument"]] = relationship(back_populates="company")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(500))
    document_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    accession_number: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    filing_type: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    filed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    parse_status: Mapped[str] = mapped_column(String(32), default="cached")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    company: Mapped[Company] = relationship(back_populates="source_documents")


class Filing(Base):
    __tablename__ = "filings"
    __table_args__ = (UniqueConstraint("company_id", "accession_number", name="uq_filing_company_accession"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    source_document_id: Mapped[int | None] = mapped_column(ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True)
    accession_number: Mapped[str] = mapped_column(String(32), index=True)
    form_type: Mapped[str] = mapped_column(String(16), index=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    primary_document: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sec_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    parse_status: Mapped[str] = mapped_column(String(32), default="cached")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped[Company] = relationship(back_populates="filings")


class EarningsReport(Base):
    __tablename__ = "earnings_reports"
    __table_args__ = (UniqueConstraint("company_id", "quarter", name="uq_earnings_report_company_quarter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    source_document_id: Mapped[int | None] = mapped_column(ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True)
    quarter: Mapped[str] = mapped_column(String(24), index=True)
    fiscal_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    parse_status: Mapped[str] = mapped_column(String(32), default="missing_manual_allowed")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class QuarterlyMetric(Base):
    __tablename__ = "quarterly_metrics"
    __table_args__ = (UniqueConstraint("company_id", "quarter", name="uq_quarterly_metric_company_quarter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    quarter: Mapped[str] = mapped_column(String(24), index=True)
    fiscal_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    share_price_used: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    enterprise_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    cash_and_equivalents: Mapped[float | None] = mapped_column(Float, nullable=True)
    subscription_revenue_growth: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_rpo_growth: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_rpo_growth_constant_currency: Mapped[float | None] = mapped_column(Float, nullable=True)
    renewal_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    gaap_net_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    non_gaap_operating_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    free_cash_flow: Mapped[float | None] = mapped_column(Float, nullable=True)
    free_cash_flow_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock_based_compensation: Mapped[float | None] = mapped_column(Float, nullable=True)
    diluted_share_count: Mapped[float | None] = mapped_column(Float, nullable=True)
    buyback_authorization_remaining: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_acv_run_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_acv_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    creator_other_share: Mapped[float | None] = mapped_column(Float, nullable=True)
    customers_over_5m_acv: Mapped[int | None] = mapped_column(Integer, nullable=True)
    named_competitive_wins: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    named_displacements: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fy_growth_guidance: Mapped[float | None] = mapped_column(Float, nullable=True)
    fy_operating_margin_guidance: Mapped[float | None] = mapped_column(Float, nullable=True)
    fy27_growth_guidance: Mapped[float | None] = mapped_column(Float, nullable=True)
    discretionary_insider_selling_depressed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    metric_sources: Mapped[dict] = mapped_column(JSON, default=dict)
    manual_fields: Mapped[list] = mapped_column(JSON, default=list)
    missing_fields: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InsiderTransaction(Base):
    __tablename__ = "insider_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    source_document_id: Mapped[int | None] = mapped_column(ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True)
    insider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    transaction_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    shares: Mapped[float | None] = mapped_column(Float, nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_discretionary: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    quarter: Mapped[str | None] = mapped_column(String(24), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    overall_signal: Mapped[str] = mapped_column(String(32), default="missing")
    conclusion: Mapped[str] = mapped_column(Text, default="")
    missing_metrics: Mapped[list] = mapped_column(JSON, default=list)
    report_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    signal_results: Mapped[list["ModelSignalResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class ModelSignalResult(Base):
    __tablename__ = "model_signal_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("model_runs.id", ondelete="CASCADE"), index=True)
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    signal_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(Text)
    triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    run: Mapped[ModelRun] = relationship(back_populates="signal_results")
