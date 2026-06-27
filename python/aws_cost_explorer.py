# ============================================================
# aws_cost_explorer.py
# Path A: month-to-date AWS cost by service (Cost Explorer API).
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# WHAT THIS IS
#   The lagged read on AWS. Convenient and fast to query, but the data
#   underneath is up to ~24h behind reality. Good for daily trends, not a
#   live tripwire.
#
# HOW TO USE
#   # Install:   pip install boto3
#   # Auth:      aws configure   (or env vars, or an instance role)
#   #
#   # Current month to today:
#   #   python aws_cost_explorer.py
#   # Explicit window (end date is exclusive):
#   #   python aws_cost_explorer.py --start 2026-06-01 --end 2026-06-17
#   #
#   # Heads up: every Cost Explorer API call costs about USD 0.01, so do
#   # not drop this in a tight polling loop.
# ============================================================

import argparse
from datetime import date

import boto3


def _month_to_date():
    today = date.today()
    return today.replace(day=1).isoformat(), today.isoformat()


def main():
    default_start, default_end = _month_to_date()
    parser = argparse.ArgumentParser(
        description="Month-to-date AWS cost by service via Cost Explorer."
    )
    parser.add_argument("--start", default=default_start,
                        help="Start date YYYY-MM-DD (inclusive).")
    parser.add_argument("--end", default=default_end,
                        help="End date YYYY-MM-DD (exclusive).")
    parser.add_argument("--region", default="us-east-1",
                        help="Cost Explorer endpoint region.")
    parser.add_argument("--granularity", default="DAILY",
                        choices=["DAILY", "MONTHLY"])
    args = parser.parse_args()

    ce = boto3.client("ce", region_name=args.region)
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": args.start, "End": args.end},
        Granularity=args.granularity,
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    for window in resp["ResultsByTime"]:
        day = window["TimePeriod"]["Start"]
        for group in window["Groups"]:
            svc = group["Keys"][0]
            amt = float(group["Metrics"]["UnblendedCost"]["Amount"])
            print(f"{day}  {svc:<32} ${amt:,.2f}")


if __name__ == "__main__":
    main()
