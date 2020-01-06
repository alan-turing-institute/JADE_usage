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
        export (str): Filename prefix to store usage data per user, group and
            account to in csv format.
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

    # Get GPU hours per user
    user_df = []
    for user in users:
        gpu_hours_user = _gpu_hours(usage[usage.User == user])
        user_df.append((user, gpu_hours_user))
    user_df = pd.DataFrame(user_df, columns=["user", "usage/GPUh"])
    user_df.sort_values("usage/GPUh", ascending=False, inplace=True)

    # Get GPU hours per group
    groups, usage = _get_groups(users, usage)
    group_df = []
    for group in groups:
        gpu_hours_group = _gpu_hours(usage[usage.Group == group])
        group_df.append((group, gpu_hours_group))
    group_df = pd.DataFrame(group_df, columns=["group", "usage/GPUh"])
    group_df.sort_values("usage/GPUh", ascending=False, inplace=True)

    # Get GPU hours per account
    account_df = []
    for account in accounts:
        gpu_hours_account = _gpu_hours(usage[usage.Account == account])
        account_df.append((account, gpu_hours_account))
    account_df = pd.DataFrame(account_df, columns=["account", "usage/GPUh"])
    account_df.sort_values("usage/GPUh", ascending=False, inplace=True)

    # Write human readable summary to stdout
    for df in [user_df, group_df, account_df]:
        _print_human_readable_table(df)

    # Write totals to stdour
    print("Total selected GPU hours: {:<,.2f}".format(gpu_hours))
    print("Total JADE GPU hours: {:<,.2f}".format(gpu_hours_total))

    # If seleced, write data to a file
    if export:
        user_df.to_csv(export+"_user.csv", index=False)
        group_df.to_csv(export+"_group.csv", index=False)
        account_df.to_csv(export+"_account.csv", index=False)
