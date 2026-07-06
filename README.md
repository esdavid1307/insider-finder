# Insider Finder

A small, open-source Python CLI that answers one question: **what was the most recent insider transaction reported for a public company?**

Give it a ticker or company name and it looks up the company on SEC EDGAR, finds the latest Form 4 filing, and prints the transaction details in a clean table — insider name, role, transaction type, shares, price, and a link to the official filing.

```bash
insider-finder AAPL
```

```text
Company: Apple Inc. (AAPL)

        Most Recent Insider Transaction
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field             ┃ Value                        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Date              │ 2026-06-15                   │
│ Insider           │ Jane Smith                   │
│ Role              │ Director                     │
│ Type              │ Sale (open market)           │
│ Code              │ S                            │
│ Shares            │ 5,000                        │
│ Price             │ $180.25                      │
│ Value             │ $901,250.00                  │
│ Acquired/Disposed │ D                            │
│ Filing            │ Form 4                       │
│ Filing URL        │ https://www.sec.gov/...      │
└───────────────────┴──────────────────────────────┘
```

## Why

Insider transactions are public information, but getting to them means clicking through EDGAR's filing indexes and reading raw Form 4 documents. This tool does that lookup in one command. It is deliberately minimal: no dashboards, no alerts, no databases, no AI — just the latest filing, fetched live from the SEC.

## Installation

Requires Python 3.11+.

```bash
git clone https://github.com/esdavid1307/insider-finder.git
cd insider-finder
python -m pip install -e ".[dev]"
```

## Usage

The company argument accepts a ticker, a company name (fuzzy-matched), or a CIK number:

```bash
insider-finder AAPL
insider-finder apple
insider-finder "Tesla"
insider-finder 320193
```

Options:

| Flag | Default | Description |
|---|---|---|
| `--days N` | 180 | How far back to look for Form 4 filings |
| `--limit N` | 1 | Number of transactions to display from the latest filing |
| `--raw` | off | Also print the raw filing metadata (useful for debugging) |

If no company matches, or no Form 4 was filed within the lookback window, the CLI prints a short message and exits cleanly rather than crashing.

### Transaction types

Form 4 reports every kind of insider transaction, not just open-market buys and sells. The CLI translates all standard SEC transaction codes into readable labels — for example `P` → Purchase (open market), `S` → Sale (open market), `M` → Option Exercise, `A` → Grant/Award, `G` → Gift. The raw code is always shown alongside the label, and unrecognized codes are displayed as-is.

## How it works

1. Resolves the company via the SEC's [company tickers list](https://www.sec.gov/files/company_tickers.json) (exact ticker/CIK match first, then name matching).
2. Fetches the company's filing history from `https://data.sec.gov/submissions/` and picks the most recent Form 4 within the lookback window.
3. Downloads the raw Form 4 XML from `https://www.sec.gov/Archives/` and parses the non-derivative transaction entries.

All data comes live from official SEC EDGAR endpoints — nothing is cached or stored.

### SEC fair access

Requests include a descriptive `User-Agent` header, as the SEC requires. If you fork this project or use it heavily, update the contact information in `insider_finder/sec_client.py` and follow the [SEC's fair access guidance](https://www.sec.gov/os/accessing-edgar-data).

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

The test suite runs entirely offline against fixture data — no network access needed.

## Contributing

Issues and small, focused pull requests are welcome. Please keep the project true to its MVP scope: one command, one answer. Dashboards, alerts, watchlists, databases, AI summaries, and trading features are out of scope.

## License

[MIT](LICENSE)

## Disclaimer

This tool is for educational and informational purposes only. It does not provide investment, legal, or financial advice. Insider transactions are reported after the fact and are frequently routine (option exercises, tax withholding, scheduled 10b5-1 sales). Always review the official SEC filings before making any decisions.
