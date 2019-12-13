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
        "date",
        type=str,
        help="The month to export usage for in the format YYYY-MM"
        )

    # Parse command line arguments
    clargs = parser.parse_args()

    if clargs.option == 'export':
        year, month = clargs.date.split("-")
        year = int(year)
        month = int(month)
        export.export(clargs.user, year, month)


if __name__ == "__main__":
    main()
