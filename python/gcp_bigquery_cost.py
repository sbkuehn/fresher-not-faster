# ============================================================
# gcp_bigquery_cost.py
# Path A: month-to-date GCP cost by service (BigQuery billing export).
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# WHAT THIS IS
#   The lagged read on GCP, and the clearest demonstration of the whole
#   idea: "the API" here is just SQL over the exported billing table. The
#   query returns instantly while the table underneath it is hours old.
#
# HOW TO USE
#   # Install:   pip install google-cloud-bigquery
#   # Auth:      gcloud auth application-default login
#   #
#   # Point at your billing export table (standard or detailed) and run:
#   #   export BILLING_EXPORT_TABLE=project.dataset.gcp_billing_export_v1_XXXX
#   #   python gcp_bigquery_cost.py
#   # Or pass it explicitly:
#   #   python gcp_bigquery_cost.py --table project.dataset.gcp_billing_export_v1_XXXX
#   #
#   # The detailed export table is named gcp_billing_export_resource_v1_*.
# ============================================================

import argparse
import os
import sys

from google.cloud import bigquery


def main():
    parser = argparse.ArgumentParser(
        description="Month-to-date GCP cost by service from the BigQuery export."
    )
    parser.add_argument(
        "--table",
        default=os.getenv("BILLING_EXPORT_TABLE"),
        help="Fully qualified export table (or set BILLING_EXPORT_TABLE).",
    )
    args = parser.parse_args()

    if not args.table:
        sys.exit("Provide --table or set BILLING_EXPORT_TABLE.")

    client = bigquery.Client()

    # The table name is supplied by the operator via flag or env var. It is
    # interpolated directly because BigQuery does not parameterize table
    # identifiers. Keep this value under your control, not user input.
    sql = f"""
        SELECT
          service.description AS service,
          ROUND(SUM(cost), 2)  AS cost
        FROM `{args.table}`
        WHERE usage_start_time >= TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH))
        GROUP BY service
        ORDER BY cost DESC
    """

    for row in client.query(sql).result():
        print(f"{row.service:<32} ${row.cost:,.2f}")


if __name__ == "__main__":
    main()
