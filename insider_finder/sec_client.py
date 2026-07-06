from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import requests

from .company_lookup import Company, companies_from_sec_payload
from .utils import clean_accession, normalize_cik, within_lookback

SEC_BASE_URL = "https://www.sec.gov"
SEC_DATA_URL = "https://data.sec.gov"
DEFAULT_USER_AGENT = (
    "insider-finder/0.1 open-source educational CLI "
    "(contact: maintainer@example.com)"
)


class SecClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class Filing:
    accession_number: str
    filing_date: str
    report_date: str | None
    form: str
    primary_document: str
    cik: str

    @property
    def filing_url(self) -> str:
        return (
            f"{SEC_BASE_URL}/Archives/edgar/data/{normalize_cik(self.cik)}/"
            f"{clean_accession(self.accession_number)}/{self.primary_document}"
        )


class SecClient:
    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, timeout: int = 20) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
            }
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 429:
            raise SecClientError("SEC rate limit reached. Please wait and try again.")
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SecClientError(f"SEC request failed: {exc}") from exc
        return response.json()

    def _get_text(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 429:
            raise SecClientError("SEC rate limit reached. Please wait and try again.")
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SecClientError(f"SEC filing request failed: {exc}") from exc
        return response.text

    def fetch_company_tickers(self) -> list[Company]:
        payload = self._get_json(f"{SEC_BASE_URL}/files/company_tickers.json")
        return companies_from_sec_payload(payload)

    def fetch_submissions(self, cik: str) -> dict[str, Any]:
        return self._get_json(f"{SEC_DATA_URL}/submissions/CIK{cik}.json")

    def fetch_filing_document(self, filing: Filing) -> str:
        return self._get_text(filing.filing_url)


def recent_form4_filings(submissions: dict[str, Any], cik: str, days: int) -> list[Filing]:
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    primary_documents = recent.get("primaryDocument", [])

    filings: list[Filing] = []
    for index, form in enumerate(forms):
        if form != "4":
            continue
        filing_date = _get_list_value(filing_dates, index)
        primary_document = _get_list_value(primary_documents, index)
        accession_number = _get_list_value(accession_numbers, index)
        if not filing_date or not primary_document or not accession_number:
            continue
        if not within_lookback(filing_date, days):
            continue
        filings.append(
            Filing(
                accession_number=accession_number,
                filing_date=filing_date,
                report_date=_get_list_value(report_dates, index),
                form=form,
                primary_document=primary_document,
                cik=cik,
            )
        )

    return sorted(filings, key=lambda filing: date.fromisoformat(filing.filing_date), reverse=True)


def _get_list_value(values: list[Any], index: int) -> Any:
    if index >= len(values):
        return None
    return values[index]
