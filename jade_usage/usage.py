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


def _get_group(username):
    """
    Get the group from a username

    Usernames are in the format <initials>-<group>. The group names are
    therefore extracted by splitting the usernames about the hyphen.
    """

    return username.split("-")[-1]


def _get_groups(users, df):
    """
    Get a unique list of groups from usernames and tag records with their
    group
    """
    groups = [_get_group(elem) for elem in users]
    groups = list(set(groups))

    df = df.assign(Group=df.User.apply(_get_group))
    return groups, df


def _print_human_readable_table(df):
    """
    Print a DataFrame in a human readable, markdown format
    """
    print(tabulate(df, headers="keys", showindex=False, tablefmt="github"))
    print("\n")


def _get_usage_by(df, column):
    """
    Product a Dataframe of GPU usage per each unique value in a column. For
    example, usage per user or account.
    """

    unique = list(df[column].unique())
    usage = []
    for value in unique:
        gpu_hours_user = _gpu_hours(df[df[column] == value])
        usage.append((value, gpu_hours_user))
    usage = pd.DataFrame(usage, columns=[column, "Usage/GPUh"])
    usage.sort_values("Usage/GPUh", ascending=False, inplace=True)

    return usage


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

    usage_total = df
    usage = usage_total
    # Filter by accounts
    if accounts:
        usage = usage[usage.Account.isin(accounts)]
    else:
        accounts = list(usage.Account.unique())

    # Filter by user names
    if users:
        usage = usage[usage.User.isin(users)]
    else:
        # Get all unique user names if a list was not supplied
        users = list(usage.User.unique())

    # Ensure usage DataFrame is not empty before continuing
    if usage.empty:
        print("No usage for the specified dates, accounts, users")
        return

    # Get total GPU hours for selected users/accounts
    gpu_hours = _gpu_hours(usage)
    # Get GPU hours for ALL of JADE
    gpu_hours_total = _gpu_hours(usage_total)

    # Get GPU hours per user, group and account
    groups, usage = _get_groups(users, usage)
    user_df = _get_usage_by(usage, "User")
    group_df = _get_usage_by(usage, "Group")
    account_df = _get_usage_by(usage, "Account")

    # Write human readable summary to stdout
    for df in [user_df, group_df, account_df]:
        _print_human_readable_table(df)

    # Write totals to stdour
    print("Total selected GPU hours: {:<,.2f}".format(gpu_hours))
    print("Total JADE GPU hours: {:<,.2f}".format(gpu_hours_total))
