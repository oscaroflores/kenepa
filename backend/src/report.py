from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from src.model.rules import Diagnosis


def write_markdown_report(reports_dir: Path, run_id: int, ticker: str, quarter: str | None, metrics: dict[str, Any], diagnosis: Diagnosis) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    quarter_slug = (quarter or "no-quarter").replace("/", "-")
    path = reports_dir / f"{ticker.upper()}-{quarter_slug}-run-{run_id}.md"
    lines = [
        f"# {ticker.upper()} Health Diagnosis",
        "",
        f"Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"Quarter: {quarter or 'missing'}",
        f"Overall signal: **{diagnosis.overall_signal.upper()}**",
        "",
        "> Not financial advice. This report shows sourced and missing data for review.",
        "",
        "## Conclusion",
        "",
        diagnosis.conclusion,
        "",
        "## Signals",
        "",
    ]
    for signal in diagnosis.signals:
        lines.extend([
            f"### {signal.signal_name}",
            "",
            f"Status: `{signal.status}`",
            "",
            signal.summary,
            "",
        ])
    lines.extend(["## Exit Signals", ""])
    lines.extend([f"- {item}" for item in diagnosis.exit_signals] or ["- None active"])
    lines.extend(["", "## Scale-In Signals", ""])
    lines.extend([f"- {item}" for item in diagnosis.scale_in_signals] or ["- None active"])
    lines.extend(["", "## Missing Metrics", ""])
    lines.extend([f"- {item}" for item in diagnosis.missing_metrics] or ["- None"])
    lines.extend(["", "## Metric Snapshot", ""])
    for key, value in sorted(metrics.items()):
        if key.startswith("_"):
            continue
        lines.append(f"- `{key}`: {value if value is not None else 'missing'}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
