"""Cell builder for segment-0-pre-flight.ipynb.

Optional pre-flight notebook the cohort runs at the top of class.
Verifies environment, SDK, API key, and that the four segment notebooks
are on disk. One green check per cell. If any cell fails, fix it BEFORE
Segment 1 starts.
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        ("md", _intro_md),
        ("code", _imports_code),
        ("code", _api_key_check_code),
        ("code", _sdk_versions_code),
        ("code", _hello_world_code),
        ("code", _mcp_json_parse_code),
        ("code", _notebooks_on_disk_code),
        ("md", _close_md),
    ]


_intro_md = """\
# Segment 0: Pre-flight

**Purpose:** verify your environment before Segment 1 starts. Run every cell top to bottom. Each cell prints a single green check or a loud failure. Fix any failure now, not mid-demo.

**What this checks**

1. `ANTHROPIC_API_KEY` is set in this kernel's environment
2. `anthropic` and `pydantic` are installed at the pinned versions
3. A hello-world Messages call returns `stop_reason="end_turn"`
4. `.mcp.json` parses as JSON
5. All five teaching notebooks are present on disk

If any cell raises, do **not** proceed to Segment 1. See `notebooks/README.md` for fixes.
"""

_imports_code = """\
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
print(f"Repo root: {REPO_ROOT}")
print(f"Python: {sys.version.split()[0]}")
"""

_api_key_check_code = """\
# Load .env if present (gitignored, never committed)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

assert os.environ.get("ANTHROPIC_API_KEY"), (
    "ANTHROPIC_API_KEY is not set. Export it in your shell or add it to .env "
    "at the repo root. See notebooks/README.md."
)
print("[OK] ANTHROPIC_API_KEY is set")
"""

_sdk_versions_code = """\
import anthropic
import pydantic

print(f"anthropic: {anthropic.__version__}")
print(f"pydantic:  {pydantic.VERSION}")

# Soft floor checks. Pinned ranges live in notebooks/requirements.txt.
assert tuple(int(p) for p in anthropic.__version__.split(".")[:2]) >= (0, 40), \\
    "anthropic SDK is too old. Run: pip install -r notebooks/requirements.txt"
assert tuple(int(p) for p in pydantic.VERSION.split(".")[:2]) >= (2, 7), \\
    "pydantic is too old. Run: pip install -r notebooks/requirements.txt"
print("[OK] SDK versions are within the pinned range")
"""

_hello_world_code = """\
from anthropic import Anthropic

client = Anthropic()
resp = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=64,
    messages=[{"role": "user", "content": "Say 'pre-flight green' and nothing else."}],
)

# Branch on stop_reason. Never parse the prose.
assert resp.stop_reason == "end_turn", f"unexpected stop_reason: {resp.stop_reason}"
print(f"model said: {resp.content[0].text}")
print(f"[OK] hello-world call returned stop_reason=end_turn")
"""

_mcp_json_parse_code = """\
mcp_path = REPO_ROOT / ".mcp.json"
assert mcp_path.exists(), f"missing: {mcp_path}"
config = json.loads(mcp_path.read_text(encoding="utf-8"))
servers = config.get("mcpServers", {})
assert servers, ".mcp.json has no mcpServers key"
print(f"[OK] .mcp.json parses, {len(servers)} servers configured: {sorted(servers)}")
"""

_notebooks_on_disk_code = """\
nb_dir = REPO_ROOT / "notebooks"
expected = [
    "segment-0-pre-flight.ipynb",
    "segment-1-customer-support-agent.ipynb",
    "segment-2-tool-design-and-mcp.ipynb",
    "segment-3-invoice-extractor.ipynb",
    "segment-4-cca-f-capstone.ipynb",
]
missing = [n for n in expected if not (nb_dir / n).exists()]
assert not missing, f"missing notebooks: {missing}"
print(f"[OK] all five teaching notebooks present in {nb_dir}")
"""

_close_md = """\
## Pre-flight green

If every cell above printed `[OK]`, you are clear to start **Segment 1**. Open `segment-1-customer-support-agent.ipynb`.

If any cell failed, fix it now. The fix is almost always one of:

- `pip install -r notebooks/requirements.txt`
- Set `ANTHROPIC_API_KEY` in this shell, then restart the kernel
- Pull the latest from the `claude-architect` repo

**Bridge:** Pre-flight is green. Segment 1 builds an agent that decides what to do. Let's go.
"""
