#!/usr/bin/env bash
# ============================================================
# aws_cost.sh
# Month-to-date AWS cost by service via the AWS CLI.
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# USAGE
#   ./aws_cost.sh                        # current month to today
#   ./aws_cost.sh 2026-06-01 2026-06-17  # explicit window (end exclusive)
#
# REQUIRES
#   AWS CLI v2, configured credentials (aws configure).
#   Note: each Cost Explorer call costs about USD 0.01.
# ============================================================
set -euo pipefail

START="${1:-$(date +%Y-%m-01)}"
END="${2:-$(date +%Y-%m-%d)}"

aws ce get-cost-and-usage \
  --time-period Start="${START}",End="${END}" \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1
