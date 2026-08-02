from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.models import Base, SourceDocument
from src.storage import apply_manual_metrics, seed_default_company


def test_manual_metrics_create_traceable_source() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        company = seed_default_company(session)
        payload = SimpleNamespace(
            quarter="FY2026-Q1",
            fiscal_year=2026,
            values={"renewal_rate": 97.0, "current_rpo_growth_constant_currency": 21.0},
            source_label="Q1 FY26 release",
            source_url="https://example.com/release",
            notes="manual test",
        )

        metric = apply_manual_metrics(session, company, payload)
        source = session.scalar(select(SourceDocument).where(SourceDocument.source_type == "manual"))

        assert metric.renewal_rate == 97.0
        assert "renewal_rate" in metric.manual_fields
        assert metric.metric_sources["renewal_rate"]["mode"] == "manual"
        assert source is not None
        assert source.document_url == "https://example.com/release"
