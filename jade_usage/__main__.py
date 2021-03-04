from . import data
from . import usage
import argparse
from datetime import date
from pathlib import Path


def get_cl_args() -> argparse.Namespace:
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Fetch and process usage data from JADE"
        )

    # Create parent parser for date range
    parent_dates = argparse.ArgumentParser(add_help=False)
    parent_dates.add_argument(
        "start",
        type=date.fromisoformat,
        help=("The earliest date (inclusive) to export data for in iso format"
              " (YYYY-MM-DD)")
    )
    parent_dates.add_argument(
        "end",
        type=date.fromisoformat,
        help=("The latest date (exclusive) to export data for in iso format"
              " (YYYY-MM-DD)")
    )

    # Add subparsers
    subparsers = parser.add_subparsers(
        description=(
            "run jade-usage <subcommand> -h for help with each subcommand"
            ),
        required=True
        )

    # Export parser
    export_parser = subparsers.add_parser(
        "export",
        parents=[parent_dates],
        help="Export job data",
        description="Export all job data in a period to a csv file"
        )
    export_parser.add_argument(
        "cluster",
        type=str,
        choices=["jade", "jade2"],
        help="Cluster to export data from. One of 'jade' or 'jade2'"
    )
    export_parser.add_argument(
        "user",
        type=str,
        help="JADE username to attempt to login as"
        )
    export_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        help="Directory to write usage data files to, (default: ./)",
        default="./"
    )
    export_parser.set_defaults(func=export_command)

    # Usage parser
    usage_parser = subparsers.add_parser(
        "usage",
        parents=[parent_dates],
        help="Display and export usage",
        description=("Display and export GPU hour usage per user, optionally"
                     " filtered by a list of usernames or accounts")
        )
    usage_parser.add_argument(
        "files",
        type=str,
        nargs='*',
        default=None,
        help=("A file, or list of files, containing usage data in the format"
              " created by the export command")
        )
    usage_parser.add_argument(
        "--accounts",
        type=str,
        nargs='*',
        default=None,
        help="Accounts to filter usage by"
        )
    usage_parser.add_argument(
        "--users",
        type=str,
        nargs='*',
        default=None,
        help="User names to filter usage by"
        )
    usage_parser.set_defaults(func=usage_command)

    # Parse command line arguments
    return parser.parse_args()


def export_command(args: argparse.Namespace) -> None:
    data.export(args.cluster, args.user, args.start, args.end, args.output_dir)


def usage_command(args: argparse.Namespace) -> None:
    df = data.import_csv(args.files)
    df = data.filter_dates(df, args.start, args.end)
    usage.usage(df, args.accounts, args.users)


def main() -> None:
    args = get_cl_args()

    args.func(args)


if __name__ == "__main__":
    main()
