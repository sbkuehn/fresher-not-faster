#!/usr/bin/env bash
# ============================================================
# azure_cost.sh
# Month-to-date Azure cost by service via the Azure CLI.
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# USAGE
#   export AZURE_SUBSCRIPTION_ID=00000000-0000-0000-0000-000000000000
#   ./azure_cost.sh
#   # or pass the subscription id as the first argument:
#   ./azure_cost.sh <sub-id>
#
# REQUIRES
#   Azure CLI (az login) and the costmanagement extension:
#     az extension add --name costmanagement
# ============================================================
set -euo pipefail

SUB="${1:-${AZURE_SUBSCRIPTION_ID:-}}"
if [[ -z "${SUB}" ]]; then
  echo "Set AZURE_SUBSCRIPTION_ID or pass a subscription id as the first argument." >&2
  exit 1
fi

az costmanagement query \
  --type ActualCost \
  --timeframe MonthToDate \
  --scope "/subscriptions/${SUB}" \
  --dataset-granularity Daily \
  --dataset-aggregation '{"totalCost":{"name":"Cost","function":"Sum"}}' \
  --dataset-grouping name=ServiceName type=Dimension
