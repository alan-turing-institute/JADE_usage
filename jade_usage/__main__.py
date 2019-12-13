from . import export
from . import usage
import argparse


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Fetch and process usage data from JADE"
        )
    # Add subparsers, sending the chose subparser to 'option'
    subparsers = parser.add_subparsers(dest='option')

    # Export parser
    export_parser = subparsers.add_parser(
        "export",
        description="Export all usage data in a period to a csv file"
        )
    export_parser.add_argument(
        "user",
        type=str,
        help="JADE username to attempt to login as"
        )
    export_parser.add_argument(
        "start_date",
        type=str,
        help="The earliest date to export usage for in the format YYYY-MM-DD"
        )
    export_parser.add_argument(
        "end_date",
        type=str,
        help="The latest date to export usage for in the format YYYY-MM-DD"
        )

    # Usage parser
    usage_parser = subparsers.add_parser(
        "usage",
        description="Display or GPU hour totals per user or project"
        )
    usage_parser.add_argument(
        "user",
        type=str,
        help="JADE username to attempt to login as"
        )
    usage_parser.add_argument(
        "start_date",
        type=str,
        help="The earliest date to export usage for in the format YYYY-MM-DD"
        )
    usage_parser.add_argument(
        "end_date",
        type=str,
        help="The latest date to export usage for in the format YYYY-MM-DD"
        )
    usage_parser.add_argument(
        "--accounts",
        type=str,
        default=None,
        help="A comma seperated list of accounts to filter usage by"
        )
    usage_parser.add_argument(
        "--users",
        type=str,
        default=None,
        help="A comma seperated list of user names to filter usage by"
        )

    # Parse command line arguments
    clargs = parser.parse_args()

    if clargs.option == 'export':
        export.export(clargs.user, clargs.start_date, clargs.end_date)
    elif clargs.option == 'usage':
        if clargs.accounts:
            accounts = clargs.accounts.split(",")
        else:
            accounts = None
        if clargs.users:
            users = clargs.users.split(",")
        else:
            users = None
        df = export.fetch(clargs.user, clargs.start_date, clargs.end_date)
        usage.usage(df, accounts, users)


if __name__ == "__main__":
    main()
