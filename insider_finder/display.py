from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .company_lookup import Company
from .parser import InsiderTransaction
from .utils import format_money, format_number

console = Console()


def show_transaction(company: Company, transaction: InsiderTransaction) -> None:
    console.print(f"[bold]Company:[/bold] {company.name} ({company.ticker})")
    console.print()

    table = Table(title="Most Recent Insider Transaction", show_lines=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    rows = [
        ("Date", transaction.transaction_date),
        ("Insider", transaction.insider_name),
        ("Role", transaction.role),
        ("Type", transaction.transaction_type),
        ("Code", transaction.transaction_code),
        ("Shares", format_number(transaction.shares)),
        ("Price", format_money(transaction.price)),
        ("Value", format_money(transaction.estimated_value)),
        ("Acquired/Disposed", transaction.acquired_disposed),
        ("Filing", "Form 4"),
        ("Filing URL", transaction.filing_url),
    ]
    for field, value in rows:
        table.add_row(field, value or "N/A")

    console.print(table)


def show_no_company(query: str) -> None:
    console.print(f'[yellow]No public company found for "{query}".[/yellow]')
    console.print("Try using a ticker symbol like AAPL.")


def show_no_form4(company: Company, days: int) -> None:
    console.print(
        f"[yellow]No Form 4 insider transaction filings found for "
        f"{company.name} in the last {days} days.[/yellow]"
    )


def show_no_transactions() -> None:
    console.print("[yellow]Found a Form 4 filing, but no parseable transaction rows were available.[/yellow]")


def show_error(message: str) -> None:
    console.print(f"[red]{message}[/red]")
