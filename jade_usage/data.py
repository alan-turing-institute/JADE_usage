from io import StringIO
import pandas as pd
from subprocess import run

FORMAT = ("jobid,jobname,account,user,partition,nodelist,reqgres,allocgres,"
          "state,exitcode,elapsed,submit,start,end")
DELIMITER = "|"
JADE_ADDRESS = "jade.hartree.stfc.ac.uk"


def _elapsed(string):
    """
    Convert an elapsed time string as output by sacct to a pandas Timedelta
    object
    """
    # split days from HH:MM:SS
    s = string.split("-")
    if len(s) == 2:
        days, remainder = s
        hours, minutes, seconds = remainder.split(":")
        return pd.Timedelta(days=int(days), hours=int(hours),
                            minutes=int(minutes), seconds=int(seconds))
    elif len(s) == 1:
        hours, minutes, seconds = s[0].split(":")
        return pd.Timedelta(hours=int(hours), minutes=int(minutes),
                            seconds=int(seconds))


def fetch(user, start_date, end_date):
    """
    Fetch usage data from JADE using the 'sacct' command over SSH.

    Args:
        user (str): The username to attempt to login as.
        start_date (str): The earliest date to get usage for in the format
            YYYY-MM-DD.
        end_date (str): The latest date to get usage for in the format
            YYYY-MM-DD.

    Returns:
        (:obj:`DataFrame`): The output of sacct as a pandas Dataframe.

    Raises:
        FetchError: If the ssh or sacct command return an error.
    """

    # Get usage data
    result = run(["ssh",
                  "{user}@{jade}".format(user=user, jade=JADE_ADDRESS),
                  "sacct",
                  "--allusers",
                  "--parsable2",
                  "--allocations",
                  "--delimiter='{}'".format(DELIMITER),
                  "--starttime={}".format(start_date),
                  "--endtime={}".format(end_date),
                  "--format={}".format(FORMAT)
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
        dayfirst=False
        )

    return df


class FetchError(Exception):
    """
    Exception raised when fetch fails
    """
    def __init__(self, result):
        message = (
            "Non zero return code when attempting to execute sacct over ssh\n"
            "command: {}\n".format(" ".join(result.args))
            + "return code: {}\n".format(result.returncode)
            + "stderr: {}\n".format(result.stderr)
        )
        super().__init__(message)


def export(user, start_date, end_date):
    """
    Export usage data from JADE to a 'csv' file (although the delimiter is
    '|'). The data is written to a file named {start_date}-{end_date}_usage.csv

    This function uses fetch.

    Args:
        user (str): The username to attempt to login as.
        start_date (str): The earliest date to get usage for in the format
            YYYY-MM-DD.
        end_date (str): The latest date to get usage for in the format
            YYYY-MM-DD.
    """
    filename = "{}-{}_usage.csv".format(start_date, end_date)

    df = fetch(user, start_date, end_date)
    df.to_csv(filename, sep=DELIMITER, index=False)


def _get_dataframe(infile):
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
        dayfirst=False
        )

    return df


def import_csv(infile):
    """
    Get a usage DataFrame from a csv, or set of csvs in the format produced by
    the export command.

    Args:
        infile (str or :obj:`list` of str): The paths of the file or files to
        import.

    Returns:
        (:obj:`DataFrame`): The output of sacct as a pandas Dataframe.
    """
    if type(infile) == list:
        return pd.concat([_get_dataframe(f) for f in infile])
    elif type(infile) == str:
        return _get_dataframe(infile)
