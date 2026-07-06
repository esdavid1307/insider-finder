from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from bs4 import BeautifulSoup, Tag

from .utils import to_decimal

# SEC Form 4 transaction codes, per the official Form 4 instructions.
TRANSACTION_TYPES = {
    "P": "Purchase (open market)",
    "S": "Sale (open market)",
    "A": "Grant/Award",
    "D": "Disposition to Issuer",
    "F": "Tax Withholding",
    "I": "Discretionary Transaction",
    "M": "Option Exercise",
    "C": "Conversion",
    "E": "Expiration (short)",
    "H": "Expiration (long)",
    "O": "Out-of-Money Exercise",
    "X": "In-the-Money Exercise",
    "G": "Gift",
    "L": "Small Acquisition",
    "W": "Will/Inheritance",
    "Z": "Voting Trust",
    "J": "Other",
    "K": "Equity Swap",
    "U": "Tender of Shares",
    "V": "Voluntarily Reported Early",
}


@dataclass(frozen=True)
class InsiderTransaction:
    insider_name: str | None
    role: str | None
    transaction_date: str | None
    transaction_code: str | None
    transaction_type: str | None
    shares: Decimal | None
    price: Decimal | None
    estimated_value: Decimal | None
    acquired_disposed: str | None
    filing_url: str


def parse_form4(xml_text: str, filing_url: str) -> list[InsiderTransaction]:
    soup = BeautifulSoup(xml_text, "xml")
    reporting_owner = soup.find("reportingOwner")
    insider_name = _text(reporting_owner, "rptOwnerName") if reporting_owner else None
    role = _extract_role(reporting_owner)

    transactions: list[InsiderTransaction] = []
    for transaction in soup.find_all("nonDerivativeTransaction"):
        code = _text(transaction, "transactionCode")
        shares = to_decimal(_text(transaction, "transactionShares"))
        price = to_decimal(_text(transaction, "transactionPricePerShare"))
        estimated_value = shares * price if shares is not None and price is not None else None
        transactions.append(
            InsiderTransaction(
                insider_name=insider_name,
                role=role,
                transaction_date=_text(transaction, "transactionDate"),
                transaction_code=code,
                transaction_type=TRANSACTION_TYPES.get(code or "", code),
                shares=shares,
                price=price,
                estimated_value=estimated_value,
                acquired_disposed=_text(transaction, "transactionAcquiredDisposedCode"),
                filing_url=filing_url,
            )
        )
    return transactions


def _text(parent: Tag | None, tag_name: str) -> str | None:
    if parent is None:
        return None
    tag = parent.find(tag_name)
    if tag is None:
        return None
    value_tag = tag.find("value")
    text = value_tag.get_text(strip=True) if value_tag else tag.get_text(strip=True)
    return text or None


def _extract_role(reporting_owner: Tag | None) -> str | None:
    if reporting_owner is None:
        return None
    relationship = reporting_owner.find("reportingOwnerRelationship")
    if relationship is None:
        return None

    roles: list[str] = []
    officer_title = _text(relationship, "officerTitle")
    if _is_true(_text(relationship, "isDirector")):
        roles.append("Director")
    if _is_true(_text(relationship, "isOfficer")):
        roles.append(officer_title or "Officer")
    if _is_true(_text(relationship, "isTenPercentOwner")):
        roles.append("10% Owner")
    if _is_true(_text(relationship, "isOther")):
        roles.append(_text(relationship, "otherText") or "Other")
    return ", ".join(roles) if roles else officer_title


def _is_true(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes"}
