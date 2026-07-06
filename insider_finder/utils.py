from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation


def normalize_cik(cik: str | int) -> str:
    return str(cik).strip().lstrip("0") or "0"


def padded_cik(cik: str | int) -> str:
    return normalize_cik(cik).zfill(10)


def clean_accession(accession_number: str) -> str:
    return accession_number.replace("-", "")


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def within_lookback(filing_date: str | None, days: int) -> bool:
    parsed = parse_date(filing_date)
    if parsed is None:
        return False
    return parsed >= date.today() - timedelta(days=days)


def to_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    stripped = value.replace(",", "").strip()
    if not stripped:
        return None
    try:
        return Decimal(stripped)
    except InvalidOperation:
        return None


def format_number(value: Decimal | int | float | None) -> str:
    if value is None:
        return "N/A"
    decimal_value = Decimal(value)
    if decimal_value == decimal_value.to_integral():
        return f"{int(decimal_value):,}"
    return f"{decimal_value:,.2f}"


def format_money(value: Decimal | int | float | None) -> str:
    if value is None:
        return "N/A"
    return f"${Decimal(value):,.2f}"
