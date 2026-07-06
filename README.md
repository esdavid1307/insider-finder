# Insider Finder

Insider Finder is a small open-source Python CLI that looks up a public company and shows the most recent reported insider transaction from SEC EDGAR Form 4 filings.

It intentionally does one thing for the MVP:

```bash
insider-finder <company_or_ticker>
```

## Installation

Requires Python 3.11 or newer.

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
insider-finder AAPL
insider-finder apple
insider-finder "Tesla"
insider-finder AAPL --days 180
insider-finder AAPL --limit 3
```

Example output:

```text
Company: Apple Inc. (AAPL)

        Most Recent Insider Transaction
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field             ┃ Value                        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Date              │ 2026-04-15                   │
│ Insider           │ Jane Smith                   │
│ Role              │ Director                     │
│ Type              │ Sale                         │
│ Code              │ S                            │
│ Shares            │ 5,000                        │
│ Price             │ $180.25                      │
│ Value             │ $901,250.00                  │
│ Acquired/Disposed │ D                            │
│ Filing            │ Form 4                       │
│ Filing URL        │ https://www.sec.gov/...      │
└───────────────────┴──────────────────────────────┘
```

If no recent Form 4 exists, the CLI prints a short message instead of failing with a traceback.

## SEC Access

The tool uses official SEC EDGAR endpoints:

- `https://www.sec.gov/files/company_tickers.json`
- `https://data.sec.gov/submissions/CIK##########.json`
- Form 4 documents from `https://www.sec.gov/Archives/`

Requests include a descriptive User-Agent header. If you fork this project for heavier use, update the User-Agent contact information and respect SEC fair-access guidance.

## Tests

```bash
pytest
```

## Contributing

Small focused pull requests are welcome. Please keep the MVP simple: no dashboards, alerts, databases, watchlists, AI summaries, or trading features.

## Disclaimer

This tool is for educational and informational purposes only. It does not provide investment, legal, or financial advice. Always review official SEC filings before making decisions.
