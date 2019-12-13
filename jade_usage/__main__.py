from . import export
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
        description="Export usage data to a csv file"
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

    # Parse command line arguments
    clargs = parser.parse_args()

    if clargs.option == 'export':
        export.export(clargs.user, clargs.start_date, clargs.end_date)


if __name__ == "__main__":
    main()
