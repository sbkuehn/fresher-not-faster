#!/usr/bin/env bash
# ============================================================
# gcp_cost.sh
# Month-to-date GCP cost by service via bq over the billing export.
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# USAGE
#   export BILLING_EXPORT_TABLE=project.dataset.gcp_billing_export_v1_XXXX
#   ./gcp_cost.sh
#   # or pass the table as the first argument:
#   ./gcp_cost.sh project.dataset.gcp_billing_export_v1_XXXX
#
# REQUIRES
#   Google Cloud SDK (gcloud + bq), authenticated.
#   GCP has no cost-query CLI, so this runs SQL over the exported table.
# ============================================================
set -euo pipefail

TABLE="${1:-${BILLING_EXPORT_TABLE:-}}"
if [[ -z "${TABLE}" ]]; then
  echo "Set BILLING_EXPORT_TABLE or pass the export table as the first argument." >&2
  exit 1
fi

bq query --use_legacy_sql=false \
"SELECT service.description AS service, ROUND(SUM(cost),2) AS cost
 FROM \`${TABLE}\`
 WHERE usage_start_time >= TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH))
 GROUP BY service
 ORDER BY cost DESC"
