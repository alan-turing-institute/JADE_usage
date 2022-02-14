from . import data
from . import report
from datetime import datetime
from pathlib import Path
import typer


app = typer.Typer()

start_argument = typer.Argument(
    ...,
    formats=["%Y-%m-%d"],
    help=("The earliest date (inclusive) to export data for in iso format"
          " (YYYY-MM-DD)")
)

end_argument = typer.Argument(
    ...,
    formats=["%Y-%m-%d"],
    help=("The latest date (exclusive) to export data for in iso format"
          " (YYYY-MM-DD)")
)


@app.command("export", help="Export all job data in a period to a csv file")
def export_command(
    start: datetime = start_argument,
    end: datetime = end_argument,
    user: str = typer.Argument(..., help="Username to attempt to login with"),
    output_dir: Path = typer.Option(
        "./",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Directory to write usage data files to, (default: ./)"
    )
) -> None:
    data.export(user, start.date(), end.date(), output_dir)


@app.command(
    "report",
    help=("Display a report of GPU hour usage, optionally filtered by a list"
          " of usernames or accounts")
)
def report_command(
    start: datetime = start_argument,
    end: datetime = end_argument,
    files: list[Path] = typer.Argument(
        ...,
        help=("A file, or list of files, containing usage data in the format"
              " created by the export command")
    ),
    account_prefix: str = typer.Option(
        None,
        help="Prefix of accounts to select"
    ),
    accounts: str = typer.Option(
        None,
        help="Comma separated list of accounts to select"
    ),
    users: str = typer.Option(
        None,
        help="Comma separated list of user names to select"
    ),
    quota: int = typer.Option(
        None,
        help="DAILY quota of GPU hours, if used your quota utilisation will be"
             " printed"
    )
) -> None:
    # Ensure list arguments are lists. Typer actually returns tuples. See
    # https://github.com/tiangolo/typer/issues/127
    files = list(files)

    if accounts is None:
        account_list = []
    else:
        account_list = accounts.split(",")

    if users is None:
        user_list = []
    else:
        user_list = users.split(",")

    df = data.import_csv(files)
    df = data.filter_dates(df, start.date(), end.date())

    elapsed_days = (end.date() - start.date()).days

    report.report(df, elapsed_days, account_prefix, account_list, user_list,
                  quota)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
