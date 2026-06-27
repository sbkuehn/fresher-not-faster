# ============================================================
# pricing.py
# Local price book for self-instrumented (Path B) cost estimation.
#
# Project : Fresher Is Not Faster (companion code)
# Author  : Shannon Eldridge-Kuehn
# Created : 2026-06-26
# Version : 1.0.0
# License : MIT
# ============================================================
#
# WHAT THIS IS
#   A small, in-process price book plus a cost function. Path B
#   estimates spend at call time by multiplying metered usage by a unit
#   price you already hold, so you never wait on the billing pipeline to
#   see a number.
#
# HOW TO USE
#   from pricing import cost_of
#   usd = cost_of("claude-sonnet", input_tokens=1200, output_tokens=350)
#
# KEEP IT FRESH
#   Treat PRICE_BOOK as a cache of the vendor list price, not gospel.
#   Refresh it on a schedule from the published pricing APIs:
#     AWS   : https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_pricing_GetProducts.html
#     Azure : https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
#     GCP   : https://cloud.google.com/billing/docs/reference/rest/v1/services.skus/list
# ============================================================

# USD per 1,000,000 tokens. These are ILLUSTRATIVE values. Replace them
# with live rates pulled from the vendor pricing APIs listed above before
# you rely on the numbers for anything that matters.
PRICE_BOOK = {
    "claude-opus":   {"input": 15.00, "output": 75.00},
    "claude-sonnet": {"input":  3.00, "output": 15.00},
    "gpt-frontier":  {"input":  5.00, "output": 15.00},
    "gemini-pro":    {"input":  1.25, "output":  5.00},
}


class UnknownModelError(KeyError):
    """Raised when a model key is not present in PRICE_BOOK."""


def cost_of(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return the estimated USD cost for a single model call.

    Args:
        model: a key present in PRICE_BOOK (a pricing label, which may
            differ from the provider's API model ID).
        input_tokens: prompt tokens reported by the provider.
        output_tokens: completion tokens reported by the provider.

    Returns:
        Estimated cost in USD at list price.

    Raises:
        UnknownModelError: if the model is not in PRICE_BOOK.
    """
    if model not in PRICE_BOOK:
        raise UnknownModelError(
            f"{model!r} is not in PRICE_BOOK. Add it, or map your API model "
            f"ID to an existing pricing key."
        )
    rates = PRICE_BOOK[model]
    return (
        (input_tokens / 1_000_000) * rates["input"]
        + (output_tokens / 1_000_000) * rates["output"]
    )


if __name__ == "__main__":
    # Quick self test:  python pricing.py
    sample = cost_of("claude-sonnet", input_tokens=1200, output_tokens=350)
    print(f"Sample claude-sonnet call: ${sample:.6f}")
