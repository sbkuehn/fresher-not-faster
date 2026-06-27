# Fresher Is Not Faster

Companion code for the article **"Fresher Is Not Faster: Why Cloud Costs Refuse to Show Up in Real Time."**

| | |
|---|---|
| **Author** | Shannon Eldridge-Kuehn |
| **Created** | June 26, 2026 |
| **Version** | 1.0.0 |
| **License** | MIT |

---

## Overview

There are two honest ways to look at cloud spend, and this repo gives you working code for both.

**Path A is the lagged read.** You query Cost Explorer on AWS, the Cost Management Query API on Azure, or the BigQuery billing export on GCP. The query returns in milliseconds, but the data underneath it is hours old, because it comes from the same billing pipeline that produces the statement of record. Path A is convenient and useful for daily trends. It is not a live tripwire.

**Path B is the live tab.** Instead of asking the provider what it billed you, you meter usage yourself at the source, multiply by a unit price you already hold, and emit the cost the instant the work happens. No billing pipeline sits in the path, so the signal is genuinely near real time. This is the only approach that can stop a runaway workload before it becomes a line item.

The two are complementary. Use Path B to steer in real time, and reconcile it against Path A (or the detailed export) once a month to measure drift.

---

## What is inside

| Path | Cloud | Python | CLI | PowerShell |
|------|-------|--------|-----|------------|
| A (lagged read) | AWS | `python/aws_cost_explorer.py` | `cli/aws_cost.sh` | `powershell/Get-AwsCost.ps1` |
| A (lagged read) | Azure | `python/azure_cost_query.py` | `cli/azure_cost.sh` | `powershell/Get-AzureCost.ps1` |
| A (lagged read) | GCP | `python/gcp_bigquery_cost.py` | `cli/gcp_cost.sh` | n/a (use `bq`) |
| B (live tab) | any | `python/token_cost_tracker.py` | n/a | n/a |

Path B is supported by two shared modules: `python/pricing.py` (the local price book) and `python/telemetry.py` (the metric emitter).

> Note on PowerShell and GCP: Google deprecated Cloud Tools for PowerShell, so the GCP path uses `bq` rather than a cmdlet.

---

## Repository structure

```
fresher-not-faster/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── python/
│   ├── pricing.py              # shared price book + cost_of()  (Path B)
│   ├── telemetry.py            # emit_metric() via OpenTelemetry (Path B)
│   ├── token_cost_tracker.py   # the live tab, with a runnable demo (Path B)
│   ├── aws_cost_explorer.py    # lagged read, AWS              (Path A)
│   ├── azure_cost_query.py     # lagged read, Azure            (Path A)
│   └── gcp_bigquery_cost.py    # lagged read, GCP              (Path A)
├── cli/
│   ├── aws_cost.sh
│   ├── azure_cost.sh
│   └── gcp_cost.sh
└── powershell/
    ├── Get-AwsCost.ps1
    └── Get-AzureCost.ps1
```

---

## Prerequisites

- Python 3.10 or newer (for the Python scripts and Path B)
- Cloud CLIs as needed: AWS CLI v2, Azure CLI, Google Cloud SDK
- PowerShell 7+ with the `Az` modules and `AWS.Tools` modules (for the PowerShell scripts)
- Credentials for whichever cloud you are querying (see Authentication below)

---

## Installation

```bash
# Clone, then create an isolated environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1

# Install the Python dependencies
pip install -r requirements.txt
```

The shell scripts have no Python dependencies. Make them executable once:

```bash
chmod +x cli/*.sh
```

---

## Authentication

Each cloud uses its standard credential chain. Nothing in this repo stores or asks for secrets.

```bash
# AWS: configure a profile, use env vars, or attach an IAM role
aws configure

# Azure: sign in; DefaultAzureCredential also accepts managed identity and env vars
az login

# GCP: set up application default credentials
gcloud auth application-default login
```

Least privilege is enough. Cost Explorer read, Cost Management reader, and BigQuery data viewer on the billing dataset cover everything here.

---

## Path A: the lagged read

The same month-to-date-by-service question, asked three ways per cloud. Pick the tool that fits where you are standing. The latency is identical across all of them.

### AWS

```bash
# Python (current month to today)
python python/aws_cost_explorer.py

# Python with an explicit window (end date is exclusive)
python python/aws_cost_explorer.py --start 2026-06-01 --end 2026-06-17

# CLI
./cli/aws_cost.sh
./cli/aws_cost.sh 2026-06-01 2026-06-17

# PowerShell
./powershell/Get-AwsCost.ps1
```

> Cost reminder: every Cost Explorer API call costs about USD 0.01, so do not poll it in a tight loop.

### Azure

```bash
# Set your subscription once
export AZURE_SUBSCRIPTION_ID=00000000-0000-0000-0000-000000000000

# Python
python python/azure_cost_query.py

# CLI (needs: az extension add --name costmanagement)
./cli/azure_cost.sh

# PowerShell
./powershell/Get-AzureCost.ps1 -SubscriptionId $env:AZURE_SUBSCRIPTION_ID
```

### GCP

```bash
# Point at your billing export table (standard or detailed)
export BILLING_EXPORT_TABLE=project.dataset.gcp_billing_export_v1_XXXX

# Python
python python/gcp_bigquery_cost.py

# CLI (runs SQL over the export via bq)
./cli/gcp_cost.sh
```

---

## Path B: the live tab

This is the near real-time signal. It runs out of the box with no API key, using simulated token usage so you can see the emitted metric immediately.

```bash
# Run the offline demo
python python/token_cost_tracker.py

# Make a real call instead (maps the model ID to a pricing key internally)
export ANTHROPIC_API_KEY=sk-ant-...
python python/token_cost_tracker.py
```

To wire it into your own service:

```python
from anthropic import Anthropic
from token_cost_tracker import tracked_completion

client = Anthropic()
resp = tracked_completion(
    client,
    model="claude-sonnet-4-6",   # the provider's API model ID
    messages=[{"role": "user", "content": "Hello"}],
    price_key="claude-sonnet",   # the PRICE_BOOK key to price against
)
```

By default the emitter records an OpenTelemetry counter and writes a structured JSON log line. To ship the metric somewhere, point the OpenTelemetry SDK at your backend. For Azure Application Insights, use the Azure Monitor distro; Datadog, Grafana, and most others accept OTLP directly.

---

## Configuration

| What | Where | Notes |
|------|-------|-------|
| Token prices | `python/pricing.py` (`PRICE_BOOK`) | Values are illustrative. Replace with live rates from the vendor pricing APIs. |
| Azure API version | `python/azure_cost_query.py` (`API_VERSION`) | Pinned to a known-good value. Check periodically for a newer stable one. |
| Subscription / table | environment variables | `AZURE_SUBSCRIPTION_ID`, `BILLING_EXPORT_TABLE` |
| Metric backend | `python/telemetry.py` | Wire the OpenTelemetry SDK to your exporter. |

The vendor pricing APIs that should feed your price book:

```text
AWS    Price List API           https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_pricing_GetProducts.html
Azure  Retail Prices API        https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
GCP    Cloud Billing Catalog    https://cloud.google.com/billing/docs/reference/rest/v1/services.skus/list
```

---

## Security notes

- Never commit credentials. The `.gitignore` already excludes the common offenders, but treat it as a backstop, not a guarantee.
- Use least-privilege, read-only roles for the cost queries.
- Path A scripts read cost data only. Path B reads token counts from your own application responses. Nothing here writes to your cloud accounts.

---

## A word on the numbers

The values in `PRICE_BOOK` are placeholders for illustration. The live tab produces a list-price estimate, which will not match your final invoice, because the statement of record accounts for discounts, commitments, credits, and taxes that your local estimate does not. That gap is expected and useful: measure it monthly and carry a correction factor forward.

---

## License

MIT. See [LICENSE](LICENSE). Swap it for your organization's preferred license if you are vendoring this internally.
