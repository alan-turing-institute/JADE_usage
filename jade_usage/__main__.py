from . import data
from . import usage
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
    cluster: data.Cluster = typer.Argument(
        ..., help="Cluster to export data from. One of 'jade' or 'jade2'"
    ),
    output_dir: Path = typer.Option(
        "./",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Directory to write usage data files to, (default: ./)"
    )
) -> None:
    data.export(cluster, user, start.date(), end.date(), output_dir)


@app.command(
    "usage",
    help=("Display and export GPU hour usage per user, optionally filtered by "
          " a list of usernames or accounts")
)
def usage_command(
    start: datetime = start_argument,
    end: datetime = end_argument,
    files: list[Path] = typer.Argument(
        ...,
        help=("A file, or list of files, containing usage data in the format"
              " created by the export command")
    ),
    account: list[str] = typer.Option(
        None,
        help="Account to filter usage by, can be specified multiple times"
    ),
    user: list[str] = typer.Option(
        None,
        help="User name to filter usage by, can be specified multiple times"
    )
) -> None:
    # Ensure list arguments are lists. Typer actually returns tuples. See
    # https://github.com/tiangolo/typer/issues/127
    files = list(files)
    accounts = list(account)
    users = list(user)

    df = data.import_csv(files)
    df = data.filter_dates(df, start.date(), end.date())
    usage.usage(df, accounts, users)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
