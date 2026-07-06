from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable

from .utils import normalize_cik, padded_cik


@dataclass(frozen=True)
class Company:
    name: str
    ticker: str
    cik: str


def companies_from_sec_payload(payload: dict) -> list[Company]:
    companies: list[Company] = []
    for item in payload.values():
        ticker = str(item.get("ticker", "")).strip().upper()
        name = str(item.get("title", "")).strip()
        cik = item.get("cik_str")
        if ticker and name and cik is not None:
            companies.append(Company(name=name, ticker=ticker, cik=padded_cik(cik)))
    return companies


def resolve_company(query: str, companies: Iterable[Company]) -> Company | None:
    normalized = query.strip().lower()
    if not normalized:
        return None

    all_companies = list(companies)
    for company in all_companies:
        if company.ticker.lower() == normalized or normalize_cik(company.cik) == normalize_cik(normalized):
            return company

    exact_name_matches = [company for company in all_companies if company.name.lower() == normalized]
    if exact_name_matches:
        return exact_name_matches[0]

    starts_with_matches = [
        company for company in all_companies if company.name.lower().startswith(normalized)
    ]
    if starts_with_matches:
        return sorted(starts_with_matches, key=lambda company: len(company.name))[0]

    contains_matches = [
        company for company in all_companies if normalized in company.name.lower()
    ]
    if contains_matches:
        return sorted(contains_matches, key=lambda company: len(company.name))[0]

    scored = [
        (SequenceMatcher(None, normalized, company.name.lower()).ratio(), company)
        for company in all_companies
    ]
    best_score, best_company = max(scored, key=lambda item: item[0], default=(0.0, None))
    if best_company and best_score >= 0.72:
        return best_company
    return None
