"""Initial schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cik", sa.String(length=16), nullable=False),
        sa.Column("fiscal_year_end", sa.String(length=8), nullable=True),
        sa.Column("ir_url", sa.String(length=500), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_companies_cik"), "companies", ["cik"], unique=True)
    op.create_index(op.f("ix_companies_ticker"), "companies", ["ticker"], unique=True)

    op.create_table(
        "source_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("document_url", sa.String(length=1000), nullable=True),
        sa.Column("local_path", sa.String(length=1000), nullable=True),
        sa.Column("accession_number", sa.String(length=32), nullable=True),
        sa.Column("filing_type", sa.String(length=16), nullable=True),
        sa.Column("filed_at", sa.Date(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("parse_status", sa.String(length=32), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index(op.f("ix_source_documents_accession_number"), "source_documents", ["accession_number"], unique=False)
    op.create_index(op.f("ix_source_documents_company_id"), "source_documents", ["company_id"], unique=False)
    op.create_index(op.f("ix_source_documents_filing_type"), "source_documents", ["filing_type"], unique=False)
    op.create_index(op.f("ix_source_documents_source_type"), "source_documents", ["source_type"], unique=False)

    op.create_table(
        "filings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("accession_number", sa.String(length=32), nullable=False),
        sa.Column("form_type", sa.String(length=16), nullable=False),
        sa.Column("filing_date", sa.Date(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("primary_document", sa.String(length=500), nullable=True),
        sa.Column("sec_url", sa.String(length=1000), nullable=True),
        sa.Column("local_path", sa.String(length=1000), nullable=True),
        sa.Column("parse_status", sa.String(length=32), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("company_id", "accession_number", name="uq_filing_company_accession"),
    )
    op.create_index(op.f("ix_filings_accession_number"), "filings", ["accession_number"], unique=False)
    op.create_index(op.f("ix_filings_company_id"), "filings", ["company_id"], unique=False)
    op.create_index(op.f("ix_filings_form_type"), "filings", ["form_type"], unique=False)

    op.create_table(
        "earnings_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("quarter", sa.String(length=24), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("parse_status", sa.String(length=32), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.UniqueConstraint("company_id", "quarter", name="uq_earnings_report_company_quarter"),
    )
    op.create_index(op.f("ix_earnings_reports_company_id"), "earnings_reports", ["company_id"], unique=False)
    op.create_index(op.f("ix_earnings_reports_quarter"), "earnings_reports", ["quarter"], unique=False)

    op.create_table(
        "quarterly_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quarter", sa.String(length=24), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("share_price_used", sa.Float(), nullable=True),
        sa.Column("market_cap", sa.Float(), nullable=True),
        sa.Column("enterprise_value", sa.Float(), nullable=True),
        sa.Column("cash_and_equivalents", sa.Float(), nullable=True),
        sa.Column("subscription_revenue_growth", sa.Float(), nullable=True),
        sa.Column("current_rpo_growth", sa.Float(), nullable=True),
        sa.Column("current_rpo_growth_constant_currency", sa.Float(), nullable=True),
        sa.Column("renewal_rate", sa.Float(), nullable=True),
        sa.Column("gaap_net_income", sa.Float(), nullable=True),
        sa.Column("non_gaap_operating_margin", sa.Float(), nullable=True),
        sa.Column("free_cash_flow", sa.Float(), nullable=True),
        sa.Column("free_cash_flow_margin", sa.Float(), nullable=True),
        sa.Column("stock_based_compensation", sa.Float(), nullable=True),
        sa.Column("diluted_share_count", sa.Float(), nullable=True),
        sa.Column("buyback_authorization_remaining", sa.Float(), nullable=True),
        sa.Column("ai_acv_run_rate", sa.Float(), nullable=True),
        sa.Column("ai_acv_target", sa.Float(), nullable=True),
        sa.Column("creator_other_share", sa.Float(), nullable=True),
        sa.Column("customers_over_5m_acv", sa.Integer(), nullable=True),
        sa.Column("named_competitive_wins", sa.Boolean(), nullable=True),
        sa.Column("named_displacements", sa.Boolean(), nullable=True),
        sa.Column("fy_growth_guidance", sa.Float(), nullable=True),
        sa.Column("fy_operating_margin_guidance", sa.Float(), nullable=True),
        sa.Column("fy27_growth_guidance", sa.Float(), nullable=True),
        sa.Column("discretionary_insider_selling_depressed", sa.Boolean(), nullable=True),
        sa.Column("metric_sources", sa.JSON(), nullable=False),
        sa.Column("manual_fields", sa.JSON(), nullable=False),
        sa.Column("missing_fields", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("company_id", "quarter", name="uq_quarterly_metric_company_quarter"),
    )
    op.create_index(op.f("ix_quarterly_metrics_company_id"), "quarterly_metrics", ["company_id"], unique=False)
    op.create_index(op.f("ix_quarterly_metrics_quarter"), "quarterly_metrics", ["quarter"], unique=False)

    op.create_table(
        "insider_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("insider_name", sa.String(length=255), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=True),
        sa.Column("transaction_type", sa.String(length=64), nullable=True),
        sa.Column("shares", sa.Float(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("is_discretionary", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index(op.f("ix_insider_transactions_company_id"), "insider_transactions", ["company_id"], unique=False)

    op.create_table(
        "model_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quarter", sa.String(length=24), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("overall_signal", sa.String(length=32), nullable=False),
        sa.Column("conclusion", sa.Text(), nullable=False),
        sa.Column("missing_metrics", sa.JSON(), nullable=False),
        sa.Column("report_path", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_model_runs_company_id"), "model_runs", ["company_id"], unique=False)
    op.create_index(op.f("ix_model_runs_created_at"), "model_runs", ["created_at"], unique=False)
    op.create_index(op.f("ix_model_runs_quarter"), "model_runs", ["quarter"], unique=False)

    op.create_table(
        "model_signal_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("model_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signal_key", sa.String(length=64), nullable=False),
        sa.Column("signal_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("triggered", sa.Boolean(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
    )
    op.create_index(op.f("ix_model_signal_results_run_id"), "model_signal_results", ["run_id"], unique=False)
    op.create_index(op.f("ix_model_signal_results_signal_key"), "model_signal_results", ["signal_key"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_model_signal_results_signal_key"), table_name="model_signal_results")
    op.drop_index(op.f("ix_model_signal_results_run_id"), table_name="model_signal_results")
    op.drop_table("model_signal_results")
    op.drop_index(op.f("ix_model_runs_quarter"), table_name="model_runs")
    op.drop_index(op.f("ix_model_runs_created_at"), table_name="model_runs")
    op.drop_index(op.f("ix_model_runs_company_id"), table_name="model_runs")
    op.drop_table("model_runs")
    op.drop_index(op.f("ix_insider_transactions_company_id"), table_name="insider_transactions")
    op.drop_table("insider_transactions")
    op.drop_index(op.f("ix_quarterly_metrics_quarter"), table_name="quarterly_metrics")
    op.drop_index(op.f("ix_quarterly_metrics_company_id"), table_name="quarterly_metrics")
    op.drop_table("quarterly_metrics")
    op.drop_index(op.f("ix_earnings_reports_quarter"), table_name="earnings_reports")
    op.drop_index(op.f("ix_earnings_reports_company_id"), table_name="earnings_reports")
    op.drop_table("earnings_reports")
    op.drop_index(op.f("ix_filings_form_type"), table_name="filings")
    op.drop_index(op.f("ix_filings_company_id"), table_name="filings")
    op.drop_index(op.f("ix_filings_accession_number"), table_name="filings")
    op.drop_table("filings")
    op.drop_index(op.f("ix_source_documents_source_type"), table_name="source_documents")
    op.drop_index(op.f("ix_source_documents_filing_type"), table_name="source_documents")
    op.drop_index(op.f("ix_source_documents_company_id"), table_name="source_documents")
    op.drop_index(op.f("ix_source_documents_accession_number"), table_name="source_documents")
    op.drop_table("source_documents")
    op.drop_index(op.f("ix_companies_ticker"), table_name="companies")
    op.drop_index(op.f("ix_companies_cik"), table_name="companies")
    op.drop_table("companies")
