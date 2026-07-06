from insider_finder.company_lookup import Company, companies_from_sec_payload, resolve_company


def test_company_lookup_works_for_known_ticker() -> None:
    companies = [
        Company(name="Apple Inc.", ticker="AAPL", cik="0000320193"),
        Company(name="Microsoft Corp", ticker="MSFT", cik="0000789019"),
    ]

    company = resolve_company("AAPL", companies)

    assert company is not None
    assert company.name == "Apple Inc."
    assert company.ticker == "AAPL"
    assert company.cik == "0000320193"


def test_company_lookup_works_for_company_name() -> None:
    companies = [
        Company(name="Apple Inc.", ticker="AAPL", cik="0000320193"),
        Company(name="Apple Hospitality REIT, Inc.", ticker="APLE", cik="0001418121"),
    ]

    company = resolve_company("apple", companies)

    assert company is not None
    assert company.ticker == "AAPL"


def test_company_lookup_handles_unknown_input() -> None:
    companies = [Company(name="Apple Inc.", ticker="AAPL", cik="0000320193")]

    assert resolve_company("not-a-company", companies) is None


def test_companies_from_sec_payload_normalizes_cik() -> None:
    payload = {
        "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    }

    companies = companies_from_sec_payload(payload)

    assert companies == [Company(name="Apple Inc.", ticker="AAPL", cik="0000320193")]
