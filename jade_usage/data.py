from __future__ import annotations
from datetime import date, datetime
from io import StringIO
import pandas as pd  # type: ignore
from pathlib import Path
from subprocess import run, CompletedProcess
from typing import Any, Union

FORMAT = ("jobid,jobname,account,user,partition,nodelist,reqgres,allocgres,"
          "state,exitcode,elapsed,submit,start,end")
DELIMITER = "|"
JADE_ADDRESS = {
    "jade": "jade.hartree.stfc.ac.uk",
    "jade2": "jade2.hartree.stfc.ac.uk"
}


def _elapsed(sacct_elapsed: str) -> pd.Timedelta:
    """
    Convert an elapsed time string as output by sacct to a pandas Timedelta
    object.
    """
    # Elapsed times are in the format [days-]HH:MM:SS[.microseconds]
    # split days from HH:MM:SS
    s = sacct_elapsed.split("-")
    if len(s) == 2:
        days, remainder = s
        hours, minutes, seconds = remainder.split(":")
        return pd.Timedelta(days=int(days), hours=int(hours),
                            minutes=int(minutes), seconds=int(seconds))
    elif len(s) == 1:
        hours, minutes, seconds = s[0].split(":")
        return pd.Timedelta(hours=int(hours), minutes=int(minutes),
                            seconds=int(seconds))


def fetch(cluster: str, user: str, start: date, end: date) -> pd.DataFrame:
    """
    Fetch usage data from JADE using the 'sacct' command over SSH.

    Args:
        cluster: The cluster to fetch data from. One of 'jade' or 'jade2'
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
                  f"{user}@{JADE_ADDRESS[cluster]}",
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


def export(cluster: str, user: str, start: date, end: date,
           output_dir: Path) -> None:
    """
    Export usage data from JADE to a 'csv' file (although the delimiter is
    '|'). The data is written to a file named {start}-{end}_usage.csv

    This function uses fetch.

    Args:
        cluster (str): The cluster to fetch data from. One of 'jade' or 'jade2'
        user (str): The username to attempt to login as.
        start (:obj:`datetime.date`): The earliest date to get usage for.
        end (:obj:`datetime.date`): The latest date to get usage for.
    """
    filename = f"{start}-{end}_usage.csv"

    df = fetch(cluster, user, start, end)
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


def import_csv(infile: Union[Path, list[Path]]) -> pd.DataFrame:
    """
    Get a usage DataFrame from a csv, or set of csvs in the format produced by
    the export command.

    Args:
        infile (str or :obj:`list` of str): The paths of the file or files to
        import.

    Returns:
        (:obj:`DataFrame`): The output of sacct as a pandas Dataframe.
    """
    if not isinstance(infile, list):
        infile = [infile]

    return pd.concat([_get_dataframe(f) for f in infile])


def filter_dates(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    start = datetime.combine(start, datetime.min.time())
    end = datetime.combine(end, datetime.min.time())

    df = df[df.Start >= start]
    df = df[df.End <= end]

    return df
