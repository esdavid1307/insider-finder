from insider_finder.sec_client import Filing


def _filing(primary_document: str) -> Filing:
    return Filing(
        accession_number="0001140361-26-025622",
        filing_date="2026-06-17",
        report_date="2026-06-15",
        form="4",
        primary_document=primary_document,
        cik="0000320193",
    )


def test_xml_url_strips_xsl_stylesheet_prefix() -> None:
    filing = _filing("xslF345X06/form4.xml")

    assert filing.xml_url == (
        "https://www.sec.gov/Archives/edgar/data/320193/000114036126025622/form4.xml"
    )
    assert filing.filing_url == (
        "https://www.sec.gov/Archives/edgar/data/320193/000114036126025622/xslF345X06/form4.xml"
    )


def test_xml_url_unchanged_without_prefix() -> None:
    filing = _filing("form4.xml")

    assert filing.xml_url == filing.filing_url
