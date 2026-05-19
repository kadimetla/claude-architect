"""Reference implementation for hooks-as-deterministic-guarantees.

Cited from COURSE-FLOW.md Segment 1. Shows the **PreToolUse** policy gate
and **PostToolUse** audit hook patterns. The point of a hook is that it
runs as *your* code, not the model's. If a guarantee must hold, hook it.
Do not put it in the prompt.

These functions are written for the bare Anthropic Messages API. The
*concept* is identical when you wire hooks into Claude Code via
``settings.json`` or via the Agent SDK's hook surface. The shape changes,
the discipline does not.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Literal

logger = logging.getLogger(__name__)

ErrorCategory = Literal["transient", "permanent", "policy"]


def make_tool_error(
    category: ErrorCategory,
    message: str,
    *,
    retryable: bool,
) -> dict[str, Any]:
    """Build a structured tool-result error payload.

    Why structured: the model reads ``errorCategory`` and ``isRetryable``
    to decide whether to retry, reformulate, or escalate. A bare error
    string forces the model to guess, and the guess is rarely the one
    you wanted.
    """
    return {
        "isError": True,
        "errorCategory": category,
        "isRetryable": retryable,
        "message": message,
    }


def enforce_refund_policy(
    tool_name: str,
    tool_input: dict[str, Any],
    *,
    cap_usd: float = 500.0,
) -> dict[str, Any] | None:
    """PreToolUse gate. Block over-cap refunds before they execute.

    Returns ``None`` when the call is allowed, or a structured error
    payload when blocked. The caller appends the error as a
    ``tool_result`` with ``is_error=True`` so the model can re-plan.

    Why a hook and not a prompt: a refund cap is a business invariant.
    Asking the prompt nicely to respect it works most of the time, which
    is the worst possible failure mode. Deterministic code, deterministic
    enforcement.
    """
    if tool_name != "process_refund":
        return None

    amount = tool_input.get("amount_usd")
    if amount is None or not isinstance(amount, (int, float)):
        return make_tool_error(
            "permanent",
            "process_refund requires a numeric amount_usd field",
            retryable=False,
        )

    if amount > cap_usd:
        logger.warning(
            "refund_policy_block",
            extra={"amount_usd": amount, "cap_usd": cap_usd},
        )
        return make_tool_error(
            "policy",
            f"Refund amount ${amount:.2f} exceeds the ${cap_usd:.2f} agent cap. "
            "Escalate to a human reviewer via escalate_to_human.",
            retryable=False,
        )

    return None


def audit_tool_call(
    tool_name: str,
    tool_input: dict[str, Any],
    tool_result: dict[str, Any] | str,
    *,
    duration_ms: float,
) -> None:
    """PostToolUse audit hook. Structured logging only, never raises.

    Why never raises: an audit hook that throws is an audit hook that
    silently disables itself the first time the model passes something
    unexpected. Log loudly, return quietly.
    """
    record = {
        "event": "tool_call",
        "tool": tool_name,
        "input": tool_input,
        "result_kind": "error" if _is_error(tool_result) else "ok",
        "duration_ms": round(duration_ms, 2),
        "ts": time.time(),
    }
    logger.info(json.dumps(record))


def _is_error(tool_result: dict[str, Any] | str) -> bool:
    return isinstance(tool_result, dict) and bool(tool_result.get("isError"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    blocked = enforce_refund_policy("process_refund", {"amount_usd": 750})
    assert blocked is not None and blocked["errorCategory"] == "policy"
    print("blocked over-cap refund:", json.dumps(blocked, indent=2))

    allowed = enforce_refund_policy("process_refund", {"amount_usd": 80})
    assert allowed is None
    print("allowed under-cap refund: (None, proceed)")

    audit_tool_call(
        "process_refund",
        {"amount_usd": 750},
        blocked,
        duration_ms=1.2,
    )
