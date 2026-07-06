from typer.testing import CliRunner

from insider_finder import cli
from insider_finder.company_lookup import Company


runner = CliRunner()


class NoResultClient:
    def fetch_company_tickers(self) -> list[Company]:
        return [Company(name="Apple Inc.", ticker="AAPL", cik="0000320193")]

    def fetch_submissions(self, cik: str) -> dict:
        return {
            "filings": {
                "recent": {
                    "form": ["10-K"],
                    "accessionNumber": ["0000320193-26-000001"],
                    "filingDate": ["2026-01-01"],
                    "reportDate": ["2025-12-31"],
                    "primaryDocument": ["aapl-20251231.htm"],
                }
            }
        }


def test_cli_handles_no_result_without_crashing(monkeypatch) -> None:
    monkeypatch.setattr(cli, "SecClient", NoResultClient)

    result = runner.invoke(cli.app, ["AAPL", "--days", "180"])

    assert result.exit_code == 0
    assert "No Form 4 insider transaction filings found" in result.output
