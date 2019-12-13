import pandas as pd
from tabulate import tabulate


def _gpu_hours(df):
    seconds_per_hour = 60.**2

    # Multiply the number of GPUs allocated (from the AllocGRES column) by the
    # elapsed number of hours
    GPU_hours = sum(
        df.AllocGRES.apply(lambda x: int(x[-1]))
        * df.Elapsed.apply(lambda x: x.seconds / seconds_per_hour)
        )
    return GPU_hours


def usage(df, accounts=None, users=None):
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
    """

    # Filter PENDING jobs
    usage_total = df[df.State != "PENDING"]
    # Filter bad GRES column entries
    # Entries should be of the format 'gpu:N' where 0<N<9 is the number of GPUs
    # allcoated
    usage_total = usage_total[usage_total.AllocGRES.isin(
        ["gpu:{}".format(i) for i in range(1, 9)])]

    usage = usage_total
    # Filter by accounts
    if accounts:
        usage = usage[usage.Account.isin(accounts)]

    # Filter by user names
    if users:
        usage = usage[usage.Account.isin(users)]
    else:
        # Get all unique user names if a list was not supplied
        users = list(usage.User.unique())
        # Remove invalid names
        users = [elem for elem in users if type(elem) == str]

    gpu_hours = _gpu_hours(usage)
    gpu_hours_total = _gpu_hours(usage_total)

    output = []
    for user in users:
        gpu_hours_user = _gpu_hours(usage[usage.User == user])
        output.append((user, gpu_hours_user))
    output = pd.DataFrame(output, columns=["user", "usage"])

    print(tabulate(output, headers="keys", showindex=False, tablefmt="github"))
    print("All users GPU hours: {:<,.2f}".format(gpu_hours))
    print("Total JADE GPU hours: {:<,.2f}".format(gpu_hours_total))
