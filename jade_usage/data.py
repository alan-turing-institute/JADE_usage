from __future__ import annotations
from datetime import date, datetime
from io import StringIO
import pandas as pd  # type: ignore
from pathlib import Path
from subprocess import run, CompletedProcess
from typing import Any

FORMAT = ("jobid,jobname,account,user,partition,nodelist,reqgres,allocgres,"
          "state,exitcode,elapsed,submit,start,end")
DELIMITER = "|"

JADE_ADDRESS = "jade2.hartree.stfc.ac.uk"


def _elapsed(sacct_elapsed: str) -> pd.Timedelta:
    """
    Convert an elapsed time string as output by sacct to a pandas Timedelta
    object.
    """
    # Elapsed times are in the format [days-]HH:MM:SS[.microseconds]
    # split days from HH:MM:SS
    s = sacct_elapsed.split("-")

    if len(s) == 2:
        days, remainder = int(s[0]), s[1]
        hours, minutes, seconds = (int(elem) for elem in remainder.split(":"))
    elif len(s) == 1:
        days = 0
        hours, minutes, seconds = (int(elem) for elem in s[0].split(":"))

    return pd.Timedelta(days=days, hours=hours, minutes=minutes,
                        seconds=seconds)


def fetch(user: str, start: date, end: date) -> pd.DataFrame:
    """
    Fetch usage data from JADE using the 'sacct' command over SSH.

    Args:
        user: The username to attempt to login as.
        start: The earliest date to get usage for.
        end: The latest date to get usage for.

    Returns:
        The output of sacct as a pandas Dataframe.

    Raises:
        FetchError: If the ssh or sacct command return an error.
    """

    # Get job data
    result = run(["ssh",
                  f"{user}@{JADE_ADDRESS}",
                  "sacct",
                  # Get job data for all users
                  "--allusers",
                  # Output data in a parsable 'csv' format without a delimiter
                  # at the end of lines
                  "--parsable2",
                  # Show only the cumulative statistics for each job (this
                  # prevents double counting elapsed time for batch or
                  # multi-stage jobs)
                  "--allocations",
                  f"--delimiter='{DELIMITER}'",
                  # When used with starttime and endtime, only jobs that were
                  # in the RUNNING state between these times. That is, only
                  # jobs which had acrued GPU usage between these times.
                  "--state=RUNNING",
                  f"--starttime={start.isoformat()}",
                  f"--endtime={end.isoformat()}",
                  # Ensure that if the job started before starttime, and/or
                  # ended after endtime that the Start and End fields are
                  # truncated to show starttime and endtime respectively
                  # (Elapsed time is also corrected to be endtime-starttime).
                  # This ensures that only usage between starttime and endtime
                  # is displayed and prevents double counting usage when a job
                  # runs over the start and end time boundaries.
                  "--truncate",
                  f"--format={FORMAT}"
                  ], capture_output=True, text=True)

    if result.returncode != 0:
        raise FetchError(result)

    f = StringIO()
    f.write(result.stdout)
    f.seek(0)
    # Declare columns to convert. Cast Elapsed column as a Timedelta
    converters = {
        'Elapsed': _elapsed
        }
    # Declare columns to parse as Datetime objects
    date_columns = [
        'Submit',
        'Start',
        'End'
        ]
    # Create Dataframe
    df = pd.read_csv(
        f,
        sep=DELIMITER,
        header=0,
        converters=converters,
        parse_dates=date_columns,
        infer_datetime_format=True,
        )

    # Remove jobs with no GPUs allocated
    df = df[df.AllocGRES.notna()]

    return df


class FetchError(Exception):
    """
    Exception raised when fetch fails
    """
    def __init__(self, result: CompletedProcess[Any]) -> None:
        message = (
            "Non zero return code when attempting to execute sacct over ssh\n"
            f"command: {' '.join(result.args)}\n"
            f"return code: {result.returncode}\n"
            f"stderr: {result.stderr}\n"
        )
        super().__init__(message)


def export(user: str, start: date, end: date, output_dir: Path) -> None:
    """
    Export usage data from JADE to a 'csv' file (although the delimiter is
    '|'). The data is written to a file named {start}-{end}_usage.csv

    This function uses fetch.

    Args:
        user: Username to attempt to login as
        start: Earliest date to get usage for
        end: Latest date to get usage for
        output_dir: Directory to store usage data csv in
    """
    filename = f"{start}-{end}_usage.csv"

    df = fetch(user, start, end)
    df.to_csv(output_dir/filename, sep=DELIMITER, index=False)


def _get_dataframe(infile: Path) -> pd.DataFrame:
    """
    Create a DataFrame from a single csv.
    """
    converters = {
        'Elapsed': pd.Timedelta
        }
    date_columns = [
        'Submit',
        'Start',
        'End'
        ]
    df = pd.read_csv(
        infile,
        sep=DELIMITER,
        header=0,
        converters=converters,
        parse_dates=date_columns,
        infer_datetime_format=True,
        )

    return df


def import_csv(infile: list[Path]) -> pd.DataFrame:
    """
    Get a usage DataFrame from a csv, or set of csvs in the format produced by
    the export command.

    Args:
        infile: paths of the files to import
    """
    return pd.concat([_get_dataframe(f) for f in infile])


def filter_dates(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Filter out entries in the DataFrame not between start and end."""
    start = datetime.combine(start, datetime.min.time())
    end = datetime.combine(end, datetime.min.time())

    df = df[df.Start >= start]
    df = df[df.End <= end]

    return df
