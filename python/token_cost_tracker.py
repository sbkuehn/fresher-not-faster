# ============================================================
# token_cost_tracker.py
# Path B: the live tab. Price an LLM call the instant it returns.
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# WHAT THIS IS
#   Wraps an LLM call, reads the token usage off the response, prices it
#   locally with pricing.cost_of, and emits the cost the moment the call
#   returns. No billing pipeline stands in the path, so the signal is
#   genuinely near real time.
#
# HOW TO USE
#   # 1. Install dependencies:
#   #      pip install -r ../requirements.txt
#   # 2. (Optional) set a real API key to make a live call:
#   #      export ANTHROPIC_API_KEY=sk-ant-...
#   # 3. Run the demo:
#   #      python token_cost_tracker.py
#   #
#   # In your own service:
#   #      from anthropic import Anthropic
#   #      from token_cost_tracker import tracked_completion
#   #      client = Anthropic()
#   #      resp = tracked_completion(client, "claude-sonnet-4-6",
#   #                                messages, price_key="claude-sonnet")
# ============================================================

import os
import time

from pricing import cost_of
from telemetry import emit_metric


def tracked_completion(client, model, messages, max_tokens=1024, price_key=None):
    """Make a completion call and emit its estimated cost as a live metric.

    Args:
        client: an LLM client exposing client.messages.create(...).
        model: the provider's API model ID used for the call.
        messages: the chat messages payload.
        max_tokens: output token ceiling for the call.
        price_key: the PRICE_BOOK key to price against. Defaults to
            ``model``. Pass this when your API model ID differs from your
            pricing label (for example "claude-sonnet-4-6" priced as
            "claude-sonnet").

    Returns:
        The provider response object, unchanged.
    """
    started = time.monotonic()
    resp = client.messages.create(
        model=model, messages=messages, max_tokens=max_tokens
    )

    usage = resp.usage
    cost = cost_of(price_key or model, usage.input_tokens, usage.output_tokens)

    # This is the near real-time cost signal. It exists the moment the
    # call returns, with no billing pipeline standing in the way.
    emit_metric(
        "llm.cost.usd",
        cost,
        {
            "model": model,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "latency_ms": round((time.monotonic() - started) * 1000),
        },
    )
    return resp


# ============================================================
# Offline demo plumbing
# ============================================================
# These stand-ins let the script run with no API key and no network call,
# so you can see the emitted metric immediately. Delete them once you wire
# in a real client.

class _FakeUsage:
    input_tokens = 1200
    output_tokens = 350


class _FakeResponse:
    usage = _FakeUsage()


class _FakeClient:
    """Stand-in client that returns simulated token usage."""

    class messages:
        @staticmethod
        def create(model, messages, max_tokens):
            time.sleep(0.05)  # pretend the model is thinking
            return _FakeResponse()


if __name__ == "__main__":
    demo_messages = [
        {"role": "user", "content": "Summarize Norse cosmology in one line."}
    ]

    if os.getenv("ANTHROPIC_API_KEY"):
        # Live path. The API model ID and the pricing key are kept separate
        # on purpose, since they often differ in practice.
        from anthropic import Anthropic

        client = Anthropic()
        tracked_completion(
            client,
            model="claude-sonnet-4-6",
            messages=demo_messages,
            price_key="claude-sonnet",
        )
    else:
        print(
            "ANTHROPIC_API_KEY not set. Running the offline demo with "
            "simulated usage.\n"
        )
        tracked_completion(_FakeClient(), model="claude-sonnet", messages=demo_messages)
