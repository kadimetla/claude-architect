"""Agent SDK hooks for compliance enforcement and data normalization.

CCA-F Domain 1, Task Statement 1.5

Key concept: hooks = deterministic. prompts = probabilistic.
Use hooks when business rules require guaranteed compliance.
"""

import datetime


def normalize_timestamps(tool_result: dict) -> dict:
    """PostToolUse hook: normalize dates to ISO 8601."""
    normalized = tool_result.copy()
    for key, value in normalized.items():
        if isinstance(value, (int, float)) and value > 1_000_000_000:
            dt = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
            normalized[key] = dt.isoformat()
    return normalized


def enforce_refund_policy(tool_name: str, tool_input: dict) -> dict | None:
    """Intercept tool calls to enforce refund limits.

    Returns None to allow, or redirect dict to block.
    Deterministic guarantee: cannot be bypassed by prompt manipulation.
    """
    if tool_name == "process_refund":
        amount = tool_input.get("amount", 0)
        if amount > 500:
            return {
                "blocked": True,
                "reason": f"Refund of ${amount} exceeds $500 limit",
                "redirect_to": "escalate_to_human",
            }
    return None


class PrerequisiteGate:
    """Block tools until prerequisites are met.

    Example: block lookup_order and process_refund until
    get_customer returns a verified ID. Solves the exam
    scenario where the agent skips verification 12% of the time.
    """

    def __init__(self):
        self.verified_customer_id = None

    def check(self, tool_name: str, tool_input: dict) -> dict | None:
        if tool_name == "get_customer":
            return None
        if tool_name in ("lookup_order", "process_refund"):
            if self.verified_customer_id is None:
                return {
                    "blocked": True,
                    "reason": "Verify customer first. Call get_customer.",
                }
        return None

    def on_tool_result(self, tool_name: str, result: dict):
        if tool_name == "get_customer" and result.get("verified"):
            self.verified_customer_id = result["customer_id"]
