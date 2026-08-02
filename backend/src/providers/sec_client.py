from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests


class SECClient:
    def __init__(self, user_agent: str, data_dir: Path, timeout: int = 30) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.sec_dir = data_dir / "raw" / "sec"
        self.sec_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov",
        }

    @staticmethod
    def cik10(cik: str) -> str:
        return str(cik).zfill(10)

    @staticmethod
    def cik_plain(cik: str) -> str:
        return str(int(str(cik)))

    def submissions_url(self, cik: str) -> str:
        return f"https://data.sec.gov/submissions/CIK{self.cik10(cik)}.json"

    def companyfacts_url(self, cik: str) -> str:
        return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{self.cik10(cik)}.json"

    def filing_document_url(self, cik: str, accession_number: str, primary_document: str) -> str:
        accession_no_dashes = accession_number.replace("-", "")
        return f"https://www.sec.gov/Archives/edgar/data/{self.cik_plain(cik)}/{accession_no_dashes}/{primary_document}"

    def _read_json_cache(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json_cache(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _get_json(self, url: str, cache_path: Path, force: bool = False) -> dict[str, Any]:
        cached = None if force else self._read_json_cache(cache_path)
        if cached is not None:
            return cached
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        self._write_json_cache(cache_path, payload)
        time.sleep(0.12)
        return payload

    def fetch_submissions(self, cik: str, force: bool = False) -> tuple[dict[str, Any], Path]:
        path = self.sec_dir / f"CIK{self.cik10(cik)}-submissions.json"
        return self._get_json(self.submissions_url(cik), path, force=force), path

    def fetch_companyfacts(self, cik: str, force: bool = False) -> tuple[dict[str, Any], Path]:
        path = self.sec_dir / f"CIK{self.cik10(cik)}-companyfacts.json"
        return self._get_json(self.companyfacts_url(cik), path, force=force), path

    def download_filing_document(
        self,
        ticker: str,
        cik: str,
        accession_number: str,
        primary_document: str,
        force: bool = False,
    ) -> tuple[Path, str]:
        url = self.filing_document_url(cik, accession_number, primary_document)
        path = self.sec_dir / ticker.upper() / accession_number.replace("-", "") / primary_document
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            return path, url
        headers = {**self.headers, "Host": "www.sec.gov"}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        path.write_bytes(response.content)
        time.sleep(0.12)
        return path, url
