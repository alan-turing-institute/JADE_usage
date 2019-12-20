import pandas as pd
from tabulate import tabulate


def _gpu_hours(df):
    seconds_per_hour = 60.**2

    # Multiply the number of GPUs allocated (from the AllocGRES column) by the
    # elapsed number of hours
    GPU_hours = sum(
        df.AllocGRES.apply(lambda x: int(x[-1]))
        * df.Elapsed.apply(lambda x: x.total_seconds() / seconds_per_hour)
        )
    return GPU_hours


def usage(df, accounts=None, users=None, export=None):
    """
    Determine usage from the data in a DataFrame

    Args:
        df (:obj:DataFrame): A Pandas DataFrame containing usage data, like
            that produced by fetch.
        accounts (:obj:`list` of :obj:`str`, optional): A list of accounts to
            include in the usage report. If None, all accounts are included.
            Default=None.
        users (:obj:`list` of :obj:`str`, optional): A list of users to
            include in the usage report. If None, all accounts are included.
            Default=None.
        export (str): Filename to store usage data per user to in csv format.
            Default=None.
    """

    usage_total = df
    usage = usage_total
    # Filter by accounts
    if accounts:
        usage = usage[usage.Account.isin(accounts)]

    # Filter by user names
    if users:
        usage = usage[usage.User.isin(users)]
    else:
        # Get all unique user names if a list was not supplied
        users = list(usage.User.unique())

    # Get total GPU hours for selected users/accounts
    gpu_hours = _gpu_hours(usage)
    # Get GPU hours for ALL of JADE
    gpu_hours_total = _gpu_hours(usage_total)

    # Get GPU hours per user
    user_df = []
    for user in users:
        gpu_hours_user = _gpu_hours(usage[usage.User == user])
        user_df.append((user, gpu_hours_user))
    user_df = pd.DataFrame(user_df, columns=["user", "usage"])

    # Write human readable summary to stdout
    print(tabulate(user_df, headers="keys", showindex=False,
                   tablefmt="github"))
    print("All users GPU hours: {:<,.2f}".format(gpu_hours))
    print("Total JADE GPU hours: {:<,.2f}".format(gpu_hours_total))

    # If seleced, write data to a file
    if export:
        user_df.to_csv(export, index=False)
