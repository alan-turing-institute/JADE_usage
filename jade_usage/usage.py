from __future__ import annotations
import pandas as pd  # type: ignore
from tabulate import tabulate
from typing import Optional, Union


def _gpu_hours(df: pd.DataFrame) -> float:
    seconds_per_hour = 60.**2

    # Multiply the number of GPUs allocated (from the AllocGRES column) by the
    # elapsed number of hours
    GPU_hours = sum(
        df.AllocGRES.apply(lambda x: int(x[-1]))
        * df.Elapsed.apply(lambda x: x.total_seconds() / seconds_per_hour)
        )
    return GPU_hours


def _get_group(username: str) -> str:
    """
    Get the group from a username

    Usernames are in the format <initials>-<group>. The group names are
    therefore extracted by splitting the usernames about the hyphen.
    """

    return username.split("-")[-1]


def _get_groups(users: list[str], df: pd.DataFrame) -> tuple[list[str],
                                                             pd.DataFrame]:
    """
    Get a unique list of groups from usernames and tag records with their
    group
    """
    groups = [_get_group(elem) for elem in users]
    groups = list(set(groups))

    df = df.assign(Group=df.User.apply(_get_group))
    return groups, df


def _get_usage_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Product a Dataframe of GPU usage per each unique value in a column. For
    example, usage per user or account.
    """

    unique = list(df[column].unique())
    usage = []
    for value in unique:
        gpu_hours_user = _gpu_hours(df[df[column] == value])
        usage.append((value, gpu_hours_user))
    usage_df = pd.DataFrame(usage, columns=[column, "Usage/GPUh"])
    usage_df.sort_values("Usage/GPUh", ascending=False, inplace=True)

    return usage_df


def usage(df: pd.DataFrame, accounts: Optional[Union[str, list[str]]] = None,
          users: Optional[Union[str, list[str]]] = None) -> None:
    """
    Determine usage from the data in a DataFrame

    Args:
        df: A Pandas DataFrame containing usage data, like that produced by
            fetch.
        accounts: A list of accounts to include in the usage report. If None,
            all accounts are included. Default=None.
        users: A list of users to include in the usage report. If None, all
            accounts are included. Default=None.
    """
    usage_total = df
    usage = usage_total
    # Filter by accounts
    if accounts:
        if not isinstance(accounts, list):
            accounts = [accounts]

        usage = usage[usage.Account.isin(accounts)]

    # Filter by user names
    if users:
        if not isinstance(users, list):
            users = [users]

        usage = usage[usage.User.isin(users)]
    else:
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
        print(
            tabulate(df, headers="keys", showindex=False, tablefmt="github"),
            end="\n\n"
        )

    # Write totals to stdour
    print("Total selected GPU hours: {:<,.2f}".format(gpu_hours))
    print("Total JADE GPU hours: {:<,.2f}".format(gpu_hours_total))
