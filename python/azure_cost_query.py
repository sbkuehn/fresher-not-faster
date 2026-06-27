# ============================================================
# azure_cost_query.py
# Path A: month-to-date Azure cost by service (Cost Management Query API).
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# WHAT THIS IS
#   The lagged read on Azure. For EA and MCA accounts the data is usually
#   8 to 24 hours behind; pay-as-you-go can be longer. Same idea, same
#   freshness ceiling as the other clouds.
#
# HOW TO USE
#   # Install:   pip install azure-identity requests
#   # Auth:      az login   (DefaultAzureCredential also accepts managed
#   #            identity, env vars, VS Code, and more)
#   #
#   # Set the subscription and run:
#   #   export AZURE_SUBSCRIPTION_ID=00000000-0000-0000-0000-000000000000
#   #   python azure_cost_query.py
#   # Or pass it explicitly:
#   #   python azure_cost_query.py --subscription <sub-id>
# ============================================================

import argparse
import os
import sys

import requests
from azure.identity import DefaultAzureCredential

# Pin a known-good API version. Check periodically for a newer stable one:
#   https://learn.microsoft.com/en-us/rest/api/cost-management/query/usage
API_VERSION = "2023-11-01"


def main():
    parser = argparse.ArgumentParser(
        description="Month-to-date Azure cost by service via the Query API."
    )
    parser.add_argument(
        "--subscription",
        default=os.getenv("AZURE_SUBSCRIPTION_ID"),
        help="Azure subscription ID (or set AZURE_SUBSCRIPTION_ID).",
    )
    args = parser.parse_args()

    if not args.subscription:
        sys.exit("Provide --subscription or set AZURE_SUBSCRIPTION_ID.")

    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default").token

    url = (
        f"https://management.azure.com/subscriptions/{args.subscription}"
        f"/providers/Microsoft.CostManagement/query?api-version={API_VERSION}"
    )
    body = {
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "Daily",
            "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
            "grouping": [{"type": "Dimension", "name": "ServiceName"}],
        },
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30,
    )
    resp.raise_for_status()

    payload = resp.json()["properties"]
    headers = [col["name"] for col in payload["columns"]]
    print("  ".join(headers))
    for row in payload["rows"]:
        print(row)


if __name__ == "__main__":
    main()
