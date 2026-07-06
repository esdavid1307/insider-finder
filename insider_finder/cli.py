from __future__ import annotations

import json

import typer

from .company_lookup import resolve_company
from .display import (
    console,
    show_error,
    show_no_company,
    show_no_form4,
    show_no_transactions,
    show_transaction,
)
from .parser import parse_form4
from .sec_client import SecClient, SecClientError, recent_form4_filings

app = typer.Typer(add_completion=False, help="Find the latest reported insider transaction.")


@app.command()
def main(
    company_or_ticker: str = typer.Argument(..., help="Public company ticker or name."),
    days: int = typer.Option(180, "--days", min=1, help="Lookback period for Form 4 filings."),
    limit: int = typer.Option(1, "--limit", min=1, help="Number of transactions to display."),
    raw: bool = typer.Option(False, "--raw", help="Show raw filing metadata for debugging."),
) -> None:
    client = SecClient()

    try:
        companies = client.fetch_company_tickers()
        company = resolve_company(company_or_ticker, companies)
        if company is None:
            show_no_company(company_or_ticker)
            raise typer.Exit(code=1)

        submissions = client.fetch_submissions(company.cik)
        filings = recent_form4_filings(submissions, company.cik, days)
        if not filings:
            show_no_form4(company, days)
            raise typer.Exit(code=0)

        filing = filings[0]
        if raw:
            console.print_json(
                json.dumps(
                    {
                        "accession_number": filing.accession_number,
                        "filing_date": filing.filing_date,
                        "report_date": filing.report_date,
                        "primary_document": filing.primary_document,
                        "filing_url": filing.filing_url,
                    }
                )
            )

        xml_text = client.fetch_filing_document(filing)
        transactions = parse_form4(xml_text, filing.filing_url)
        if not transactions:
            show_no_transactions()
            raise typer.Exit(code=0)

        for transaction in transactions[:limit]:
            show_transaction(company, transaction)
    except SecClientError as exc:
        show_error(str(exc))
        raise typer.Exit(code=1) from exc
    except OSError as exc:
        show_error(f"Could not connect to SEC EDGAR. Check your internet connection and try again. ({exc})")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
