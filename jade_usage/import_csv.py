import pandas as pd
from .export import DELIMITER


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
