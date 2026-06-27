# ============================================================
# telemetry.py
# Thin metric emitter for the live cost signal (Path B).
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# WHAT THIS IS
#   A small emit_metric() wrapper. By default it records an OpenTelemetry
#   counter AND writes a structured JSON log line, so the signal is usable
#   whether or not you have wired up an exporter yet.
#
# HOW TO USE
#   from telemetry import emit_metric
#   emit_metric("llm.cost.usd", 0.0123, {"model": "claude-sonnet"})
#
# SHIP IT SOMEWHERE
#   Point the OpenTelemetry SDK at your backend. For Azure Application
#   Insights, use the Azure Monitor OpenTelemetry distro:
#     https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable
#   Datadog, Grafana, and most others accept OTLP directly.
# ============================================================

import json
import logging

# OpenTelemetry is optional. If it is not installed or not configured, we
# still emit a structured log line so nothing is silently lost.
try:
    from opentelemetry import metrics

    _meter = metrics.get_meter("finops.tokens")
    _cost_counter = _meter.create_counter("llm.cost.usd", unit="USD")
except Exception:  # noqa: BLE001 (broad on purpose: telemetry must never crash callers)
    _cost_counter = None

logging.basicConfig(level=logging.INFO, format="%(message)s")
_log = logging.getLogger("finops.tokens")


def emit_metric(name: str, value: float, attributes: dict) -> None:
    """Emit a single cost metric to telemetry and to structured logs.

    Args:
        name: metric name, for example "llm.cost.usd".
        value: the numeric value to record.
        attributes: dimensions to attach (model, tokens, latency, etc.).
    """
    if _cost_counter is not None:
        _cost_counter.add(value, attributes)
    _log.info(json.dumps({"metric": name, "value": value, **attributes}))
