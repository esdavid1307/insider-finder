from decimal import Decimal
from pathlib import Path

from insider_finder.parser import parse_form4


FIXTURE = Path(__file__).parent / "fixtures" / "form4_purchase_sale.xml"


def test_parser_extracts_insider_name_and_transaction_date() -> None:
    transactions = parse_form4(FIXTURE.read_text(), "https://www.sec.gov/example")

    assert transactions[0].insider_name == "Jane Smith"
    assert transactions[0].role == "Director"
    assert transactions[0].transaction_date == "2026-04-15"


def test_parser_maps_purchase_and_calculates_estimated_value() -> None:
    transactions = parse_form4(FIXTURE.read_text(), "https://www.sec.gov/example")

    assert transactions[0].transaction_code == "P"
    assert transactions[0].transaction_type == "Purchase (open market)"
    assert transactions[0].shares == Decimal("100")
    assert transactions[0].price == Decimal("12.50")
    assert transactions[0].estimated_value == Decimal("1250.00")
    assert transactions[0].acquired_disposed == "A"


def test_parser_maps_sale() -> None:
    transactions = parse_form4(FIXTURE.read_text(), "https://www.sec.gov/example")

    assert transactions[1].transaction_code == "S"
    assert transactions[1].transaction_type == "Sale (open market)"
    assert transactions[1].estimated_value == Decimal("500")


def test_parser_labels_option_exercise_and_falls_back_to_raw_code() -> None:
    xml = FIXTURE.read_text()

    exercise = parse_form4(xml.replace(">P<", ">M<", 1), "https://www.sec.gov/example")
    assert exercise[0].transaction_type == "Option Exercise"

    unknown = parse_form4(xml.replace(">P<", ">Q<", 1), "https://www.sec.gov/example")
    assert unknown[0].transaction_type == "Q"
