from . import data
from . import usage
from datetime import datetime
from enum import Enum
from pathlib import Path
import typer


class Cluster(Enum):
    jade = "jade"
    jade2 = "jade2"


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
    cluster: Cluster = typer.Argument(
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
    start = start.date()
    end = end.date()
    data.export(cluster, user, start, end, output_dir)


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
    accounts: list[str] = typer.Option(
        [], help="Accounts to filter usage by"
    ),
    users: list[str] = typer.Option(
        None, help="User names to filter usage by"
    )
) -> None:
    # Ensure list arguments are lists. See
    # https://github.com/tiangolo/typer/issues/127
    files = list(files)
    accounts = list(accounts)
    users = list(users)
    start = start.date()
    end = end.date()
    df = data.import_csv(files)
    df = data.filter_dates(df, start, end)
    usage.usage(df, accounts, users)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
