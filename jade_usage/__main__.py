from . import data
from . import usage
import argparse
from datetime import date


def get_cl_args():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Fetch and process usage data from JADE"
        )

    # Create parent parser for date range
    parent_dates = argparse.ArgumentParser(add_help=False)
    parent_dates.add_argument(
        "start_date",
        type=date.fromisoformat,
        help=("The earliest date (inclusive) to export data for in iso format"
              " (YYYY-MM-DD)")
    )
    parent_dates.add_argument(
        "end_date",
        type=date.fromisoformat,
        help=("The latest date (exclusive) to export data for in iso format"
              " (YYYY-MM-DD)")
    )

    # Add subparsers, sending the chose subparser to 'option'
    subparsers = parser.add_subparsers(
        description=(
            "run jade-usage <subcommand> -h for help with each subcommand"
            ),
        dest='option',
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
    usage_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Filename prefix to write usage to"
        )

    # Parse command line arguments
    return parser.parse_args()


def main():
    clargs = get_cl_args()

    if clargs.option == 'export':
        data.export(clargs.cluster, clargs.user, clargs.start_date,
                    clargs.end_date)
    elif clargs.option == 'usage':
        df = data.import_csv(clargs.files)
        df = data.filter_dates(df, clargs.start_date, clargs.end_date)
        usage.usage(df, clargs.accounts, clargs.users, clargs.output)


if __name__ == "__main__":
    main()
