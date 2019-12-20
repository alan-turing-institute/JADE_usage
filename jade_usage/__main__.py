from . import data
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
        description=(
            "Display and export GPU hour usage per user, optionally filtered"
            "by a list of usernames or accounts"
            )
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
        "--user",
        type=str,
        default=None,
        help=("JADE username to attempt to login as, if used usage data is"
              "fetched from JADE. Incompatible with --file")
        )
    usage_parser.add_argument(
        "--file",
        type=str,
        nargs='*',
        default=None,
        help=("A file, or list of files, containing usage data in the format"
              "created by the export command. Incompatible with --user")
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
        help="Path or filename to write usage to"
        )

    # Parse command line arguments
    clargs = parser.parse_args()

    if clargs.option == 'export':
        data.export(clargs.user, clargs.start_date, clargs.end_date)
    elif clargs.option == 'usage':
        if (clargs.user is not None) and (clargs.file is not None):
            raise Exception("Only one of --user and --file should be defined")

        if clargs.user:
            df = data.fetch(clargs.user, clargs.start_date, clargs.end_date)
        elif clargs.file:
            df = data.import_csv(clargs.file)
        else:
            raise Exception("One of --user and --file should be defined")
        usage.usage(df, clargs.accounts, clargs.users, clargs.output)


if __name__ == "__main__":
    main()
