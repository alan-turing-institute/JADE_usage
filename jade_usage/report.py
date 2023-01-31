from __future__ import annotations
import pandas as pd  # type: ignore
from tabulate import tabulate
from typing import Optional


JADE_DAILY_CAPACITY = 12096


def _get_group(username: str) -> str:
    """
    Get the group from a username

    Usernames are in the format <initials>-<group>. The group names are
    therefore extracted by splitting the usernames about the hyphen.
    """

    return username.split("-")[-1]


def _get_usage_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Produce a Dataframe of GPU usage per each unique value in a column. For
    example, usage per user or account.

    Args:
        df: DataFrame to filter
        column: Header of the column
    """

    # Sum GPUh for unique values in 'column'
    usage_df = df[[column, 'gpuh']].groupby(column).sum()

    # Get total GPUh for every entry
    total_usage = usage_df['gpuh'].sum()

    # Add column for % usage
    usage_df = usage_df.assign(gpupercent=usage_df['gpuh'].apply(
        lambda x: x/total_usage*100
    ))

    usage_df.sort_values("gpuh", ascending=False, inplace=True)

    usage_df = usage_df.rename(columns={
        "gpuh": "Usage / GPUh",
        "gpupercent": "Usage / %"
    })

    return usage_df


def report(usage: pd.DataFrame, elapsed_days: int,
           account_prefix: Optional[str], accounts: Optional[list[str]],
           users: Optional[list[str]], quota: Optional[int] = None) -> None:
    """
    Produce usage report using the data in a DataFrame

    Args:
        usage: DataFrame containing usage data, like that produced by fetch.
        elapsed_days: The number of days covered in the dataframe.
        account_prefix: Prefix of accounts to include in the usage report. If
            None, all accounts are included. Applied before `accounts`.
        accounts: List of accounts to include in the usage report. If None,
            all accounts are included. Applied after `account_prefix`.
        users: List of users to include in the usage report. If None, all
            users are included.
        quota: User defined daily GPU hour quota. If supplied utilisation
            against this quota will be reported.
    """
    usage_total = usage

    # Filter by account prefix
    if account_prefix:
        usage = usage.query("Account.str.startswith(@account_prefix)")

    # Filter by accounts
    if accounts:
        usage = usage.query("Account.isin(@accounts)")

    # Filter by user names
    if users:
        usage = usage.query("User.isin(@users)")

    # Ensure usage DataFrame is not empty before continuing
    if usage.empty:
        print("No usage for the specified dates, accounts, users")
        return

    # Get total GPU hours for selected users/accounts
    gpu_hours = usage['gpuh'].sum()
    # Get GPU hours for ALL of JADE
    gpu_hours_total = usage_total['gpuh'].sum()

    # Add group column to usage data
    usage = usage.assign(Group=usage.User.apply(_get_group))

    # Get GPU hours per user, group, account and allocated resources
    user_df = _get_usage_by(usage, "User")
    group_df = _get_usage_by(usage, "Group")
    account_df = _get_usage_by(usage, "Account")
    gpu_df = _get_usage_by(usage, "ngpu")
    gpu_df = gpu_df.rename_axis("GPUs")

    # Print human readable summary of usage DataFrames
    for df in [user_df, group_df, account_df, gpu_df]:
        print(
            tabulate(df, headers="keys", showindex=True, tablefmt="github"),
            end="\n\n"
        )

    selected_utilisation = (gpu_hours / elapsed_days / JADE_DAILY_CAPACITY)
    total_utilisation = (gpu_hours_total / elapsed_days / JADE_DAILY_CAPACITY)

    print(f"Selected GPU hours used: {gpu_hours:.2f}")
    print(f"Selected utilisation: {selected_utilisation*100:.2f}%")
    print(f"Total GPU hours used: {gpu_hours_total:.2f}")
    print(f"Total utilisation: {total_utilisation*100:.2f}%")
    if quota:
        quota_utilisation = (gpu_hours / elapsed_days / quota)
        print(f"Quota utilisation: {quota_utilisation*100:.2f}%")
