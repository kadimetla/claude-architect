"""Generate the 8 hero infographics for the Claude Architect Foundations deck.

Each function returns a self-contained SVG string sized for 1920x1080 (16:9).
After writing the SVG to images/infographics/, we render to PNG at 2x via
cairosvg so the image embeds crisply at projector resolution and on Zoom share.

Accessibility rules (apply to every infographic):
  - No color-only encoding. Binary contrasts use blue vs. orange, not red/green.
  - Minimum text size 22pt at 1920x1080 (so it survives a projector and Zoom).
  - Bold key terms wherever the eye should land first.
  - Decorative shapes never carry meaning that the text labels do not also carry.

Palette (committed in PALETTE dict below):
  navy        #0F2A47   primary backgrounds, headers
  ice         #E8EEF7   light backgrounds, contrast against navy
  cream       #F8F4EC   warm neutral panel fill
  gold        #F2A93B   emphasis, "this is the point" callouts
  teal        #1FA8B3   one half of a binary contrast (cooperates with gold)
  slate       #3D6BB1   secondary accent, calm structure (paired with gold)
  warm        #D85A2A   warning / "fail closed" callouts (red/green safe)
  ink         #1A2235   primary body text on light surfaces
  mist        #6B7A91   secondary text on light surfaces
  white       #FFFFFF   text on dark surfaces

Run:
    python scripts/_infographics/build.py

Outputs:
    images/infographics/*.svg   (source of truth, version-controlled)
    images/infographics/*.png   (1920x1080 @ 2x = 3840x2160, embedded by deck)
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import cairosvg
except ImportError:
    print("ERROR: cairosvg missing. Run: pip install cairosvg", file=sys.stderr)
    sys.exit(1)


def esc(s: str) -> str:
    """Escape text for safe insertion into SVG <text> elements.

    SVG is XML.  Unescaped <, >, & break the parse silently in some renderers
    and loudly in cairosvg.  We swap them for entities while leaving the rest
    of the string alone (no quote-escape needed because we only ever inline
    these into element bodies, never attribute values).
    """
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


PALETTE = {
    "navy":  "#0F2A47",
    "ice":   "#E8EEF7",
    "cream": "#F8F4EC",
    "gold":  "#F2A93B",
    "teal":  "#1FA8B3",
    "slate": "#3D6BB1",
    "warm":  "#D85A2A",
    "ink":   "#1A2235",
    "mist":  "#6B7A91",
    "white": "#FFFFFF",
}

# Shared font stack: Segoe UI is Windows-native and renders identically on Tim's
# machine and the cohort's machines. Fallback chain keeps it pleasant on macOS
# and Linux for the recorded version.
FONT_STACK = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', 'Menlo', monospace"


def svg_open(width: int = 1920, height: int = 1080, bg: str = "ice") -> str:
    """Return the SVG opening with viewBox and background fill."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="{PALETTE[bg]}"/>
"""


def title_band(text: str, subtitle: str = "", bg_color: str = "navy") -> str:
    """Return a top title bar: 1920 wide, 110 tall, dark with white text."""
    sub = ""
    if subtitle:
        sub = f"""
  <text x="60" y="92" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{PALETTE['gold']}" letter-spacing="2">{subtitle.upper()}</text>"""
    return f"""
  <rect x="0" y="0" width="1920" height="120" fill="{PALETTE[bg_color]}"/>
  <text x="60" y="62" font-family="{FONT_STACK}" font-size="44" font-weight="700"
        fill="{PALETTE['white']}">{text}</text>{sub}
"""


def footer(domain: str, segment: str) -> str:
    """Return the bottom-left domain tag + bottom-right segment tag."""
    return f"""
  <rect x="0" y="1030" width="1920" height="50" fill="{PALETTE['navy']}" opacity="0.92"/>
  <text x="60" y="1065" font-family="{FONT_STACK}" font-size="20" font-weight="600"
        fill="{PALETTE['gold']}" letter-spacing="1">{domain.upper()}</text>
  <text x="1860" y="1065" font-family="{FONT_STACK}" font-size="20" font-weight="400"
        fill="{PALETTE['white']}" text-anchor="end">{segment}</text>
"""


# ---------------------------------------------------------------------------
# 1. The Agentic Loop - stop_reason state machine
# ---------------------------------------------------------------------------

def agentic_loop() -> str:
    """Central 'Your code' node with 6 stop_reason branches.

    Layout: central rounded square (your code), six radiating cards for each
    stop_reason value. Each card carries the value name + the action you take.
    """
    P = PALETTE
    svg = svg_open()
    svg += title_band("The agentic loop is a state machine", "Domain 1  -  Branch on the enum, never on prose")

    # Center node - "Your code"
    cx, cy = 960, 545
    svg += f"""
  <rect x="{cx-180}" y="{cy-90}" width="360" height="180" rx="18" fill="{P['navy']}" stroke="{P['gold']}" stroke-width="4"/>
  <text x="{cx}" y="{cy-30}" font-family="{FONT_STACK}" font-size="34" font-weight="700"
        fill="{P['white']}" text-anchor="middle">Your code</text>
  <text x="{cx}" y="{cy+10}" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['ice']}" text-anchor="middle">reads response.stop_reason</text>
  <text x="{cx}" y="{cy+45}" font-family="{FONT_MONO}" font-size="20" font-weight="700"
        fill="{P['gold']}" text-anchor="middle">switch (stop_reason)</text>
"""

    # 6 branches: (value, action, color, dx, dy)
    branches = [
        ("end_turn",     "Return to user",                  "teal",  -700, -270),
        ("tool_use",     "Execute tool, append result, loop", "gold",  -700,    0),
        ("pause_turn",   "Resume in next request",          "slate", -700,  270),
        ("max_tokens",   "Continue or surface limit",       "slate",  340, -270),
        ("stop_sequence","Honor the sequence, end turn",    "teal",   340,    0),
        ("refusal",      "Surface category (cyber / bio)",  "warm",   340,  270),
    ]

    for value, action, color, dx, dy in branches:
        bx, by = cx + dx, cy + dy
        # Connector line from center to box
        # Compute attach point on center box edge
        if dx < 0:
            line_x1 = cx - 180
            line_x2 = bx + 360
        else:
            line_x1 = cx + 180
            line_x2 = bx
        line_y = cy + dy * 0.0  # straight to center vertically; will adjust
        svg += f"""
  <path d="M {line_x1} {cy} C {(line_x1+line_x2)/2} {cy}, {(line_x1+line_x2)/2} {by+45}, {line_x2} {by+45}"
        stroke="{P[color]}" stroke-width="3" fill="none" stroke-linecap="round"/>
"""
        # Branch card
        svg += f"""
  <rect x="{bx}" y="{by}" width="360" height="90" rx="10" fill="{P['white']}" stroke="{P[color]}" stroke-width="3"/>
  <rect x="{bx}" y="{by}" width="14" height="90" rx="0" fill="{P[color]}"/>
  <text x="{bx+35}" y="{by+38}" font-family="{FONT_MONO}" font-size="26" font-weight="700"
        fill="{P['ink']}">{value}</text>
  <text x="{bx+35}" y="{by+68}" font-family="{FONT_STACK}" font-size="20" font-weight="400"
        fill="{P['mist']}">{action}</text>
"""

    # Anti-pattern callout
    svg += f"""
  <rect x="60" y="940" width="1800" height="70" rx="8" fill="{P['warm']}" opacity="0.15"/>
  <rect x="60" y="940" width="14" height="70" fill="{P['warm']}"/>
  <text x="90" y="985" font-family="{FONT_STACK}" font-size="24" font-weight="600" fill="{P['ink']}">
    Anti-pattern:  parsing natural-language signals.  "It said thanks, so I assume it's done."  That is how production agents go feral.
  </text>
"""

    svg += footer("Domain 1 - Agentic Architecture (27%)", "Segment 1")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 2. Defense-in-Depth Layers - prompt / description / hook
# ---------------------------------------------------------------------------

def defense_in_depth() -> str:
    """Three horizontal bands stacked, soft (top) to hard (bottom) guarantees."""
    P = PALETTE
    svg = svg_open()
    svg += title_band("Defense in depth: three layers, three strengths",
                      "Domain 1  -  The prompt advises.  The hook enforces.")

    # Layers - three horizontal bands
    # Band 1: Prompt
    svg += f"""
  <rect x="160" y="190" width="1600" height="220" rx="14" fill="{P['white']}" stroke="{P['slate']}" stroke-width="3"/>
  <rect x="160" y="190" width="22" height="220" fill="{P['slate']}"/>
  <text x="220" y="240" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['slate']}" letter-spacing="2">LAYER 1  -  SOFT</text>
  <text x="220" y="290" font-family="{FONT_STACK}" font-size="40" font-weight="700"
        fill="{P['ink']}">Prompt</text>
  <text x="220" y="335" font-family="{FONT_STACK}" font-size="24" font-weight="400"
        fill="{P['ink']}">"Do not exceed the refund cap."  -  Model reads it, usually cooperates, occasionally negotiates.</text>
  <text x="220" y="378" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['mist']}">Best for:  intent, tone, formatting.  Worst for:  guarantees you cannot afford to lose.</text>
"""

    # Band 2: Tool description
    svg += f"""
  <rect x="160" y="450" width="1600" height="220" rx="14" fill="{P['white']}" stroke="{P['teal']}" stroke-width="3"/>
  <rect x="160" y="450" width="22" height="220" fill="{P['teal']}"/>
  <text x="220" y="500" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['teal']}" letter-spacing="2">LAYER 2  -  STRUCTURAL</text>
  <text x="220" y="550" font-family="{FONT_STACK}" font-size="40" font-weight="700"
        fill="{P['ink']}">Tool description + input_schema</text>
  <text x="220" y="595" font-family="{FONT_STACK}" font-size="24" font-weight="400"
        fill="{P['ink']}">"amount_cents:  integer, max 50000."  Schema rejects bad shapes.  Description shapes intent.</text>
  <text x="220" y="638" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['mist']}">Best for:  input validation, "when to call vs. when not to."  Worst for:  business-policy enforcement.</text>
"""

    # Band 3: Hook
    svg += f"""
  <rect x="160" y="710" width="1600" height="220" rx="14" fill="{P['navy']}" stroke="{P['gold']}" stroke-width="4"/>
  <rect x="160" y="710" width="22" height="220" fill="{P['gold']}"/>
  <text x="220" y="760" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['gold']}" letter-spacing="2">LAYER 3  -  HARD</text>
  <text x="220" y="810" font-family="{FONT_STACK}" font-size="40" font-weight="700"
        fill="{P['white']}">PreToolUse hook</text>
  <text x="220" y="855" font-family="{FONT_STACK}" font-size="24" font-weight="400"
        fill="{P['ice']}">if amount &gt; 50000:  permissionDecision = "deny."  Your code, your call.  The model cannot route around it.</text>
  <text x="220" y="898" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['ice']}">Best for:  policy, compliance, audit, anything that MUST hold.  Fail closed when the hook itself errors.</text>
"""

    svg += footer("Domain 1 - Hooks and deterministic guarantees", "Segment 1")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 3. Three-Tier Tool Taxonomy - server / MCP / harness
# ---------------------------------------------------------------------------

def three_tier_tools() -> str:
    """Three vertical columns. Server | MCP | Harness, with comparison rows."""
    P = PALETTE
    svg = svg_open()
    svg += title_band("Three tiers tools come from",
                      "Domain 2  -  Same noun, different runtime, different expectations")

    # Three columns
    col_specs = [
        ("Tier 1", "Server tools",     "Anthropic-hosted",    "teal",
         [("Runtime",        "Anthropic's servers"),
          ("Discovery",      "Register by type"),
          ("Examples",       "bash_20250124, code_execution, web_search"),
          ("Loop ownership", "Anthropic executes server-side")]),
        ("Tier 2", "MCP tools",        "You or vendor host",   "gold",
         [("Runtime",        "Your process or remote vendor"),
          ("Discovery",      "list_tools() at runtime"),
          ("Examples",       "Filesystem, GitHub, Sentry, your own"),
          ("Loop ownership", "You execute, append tool_result")]),
        ("Tier 3", "Harness tools",    "Claude Code only",    "slate",
         [("Runtime",        "Claude Code TypeScript harness"),
          ("Discovery",      "Built into the CLI"),
          ("Examples",       "Read, Edit, Bash, Grep (Claude Code)"),
          ("Loop ownership", "Not API-reachable.  Same noun, different sandbox.")]),
    ]

    col_w = 540
    gap = 30
    start_x = (1920 - (col_w * 3 + gap * 2)) // 2

    for i, (tier_label, name, sub, color, rows) in enumerate(col_specs):
        x = start_x + i * (col_w + gap)
        # Card
        svg += f"""
  <rect x="{x}" y="180" width="{col_w}" height="780" rx="14" fill="{P['white']}" stroke="{P[color]}" stroke-width="4"/>
  <rect x="{x}" y="180" width="{col_w}" height="160" rx="14" fill="{P[color]}"/>
  <rect x="{x}" y="320" width="{col_w}" height="20" fill="{P[color]}"/>
  <text x="{x + col_w//2}" y="235" font-family="{FONT_STACK}" font-size="26" font-weight="600"
        fill="{P['white']}" text-anchor="middle" letter-spacing="3">{tier_label.upper()}</text>
  <text x="{x + col_w//2}" y="290" font-family="{FONT_STACK}" font-size="42" font-weight="700"
        fill="{P['white']}" text-anchor="middle">{name}</text>
  <text x="{x + col_w//2}" y="325" font-family="{FONT_STACK}" font-size="20" font-weight="400"
        fill="{P['white']}" text-anchor="middle" opacity="0.92">{sub}</text>
"""
        # Comparison rows
        row_y = 380
        for label, val in rows:
            svg += f"""
  <text x="{x + 30}" y="{row_y}" font-family="{FONT_STACK}" font-size="18" font-weight="600"
        fill="{P[color]}" letter-spacing="1">{label.upper()}</text>
  <text x="{x + 30}" y="{row_y + 32}" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['ink']}">{val}</text>
"""
            row_y += 88

    # The trap callout
    svg += f"""
  <rect x="60" y="985" width="1800" height="36" rx="6" fill="{P['gold']}" opacity="0.18"/>
  <text x="80" y="1010" font-family="{FONT_STACK}" font-size="20" font-weight="600" fill="{P['ink']}">
    The trap that catches working architects:  registering "bash" in a custom agent and expecting harness behavior.  Same noun.  Different runtime.
  </text>
"""

    svg += footer("Domain 2 - Tool Design and MCP (18%)", "Segment 2  /  Segment 2.5")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 4. MCP Transport Matrix - stdio / SSE / HTTP
# ---------------------------------------------------------------------------

def mcp_transports() -> str:
    """4x3 matrix: Transport (rows) x Property (cols)."""
    P = PALETTE
    svg = svg_open()
    svg += title_band("MCP transports - one config shape, three runtimes",
                      "Domain 2  -  .mcp.json speaks stdio, SSE, and HTTP")

    # Column headers
    # NOTE: column widths sized so the longest cell text (the auth header
    # value with $&#123;API_TOKEN&#125; tokens, ~70 chars) fits at 22pt.
    # 460px per column, label col 200px = total 2040 - centered inside 1920.
    # We pull start_x left to 80 so the whole table fits with 80px margins.
    cols = ["Network", "Config keys", "Auth pattern", "When to pick it"]
    col_w = 410
    label_col_w = 200
    start_x = 60
    header_y = 200
    row_h = 180

    # Header band
    svg += f"""
  <rect x="{start_x}" y="{header_y}" width="{label_col_w + col_w * 4}" height="80" fill="{P['navy']}"/>
"""
    # Header text
    svg += f"""
  <text x="{start_x + label_col_w//2}" y="{header_y + 50}" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['gold']}" text-anchor="middle" letter-spacing="2">TRANSPORT</text>
"""
    for i, ch in enumerate(cols):
        cx = start_x + label_col_w + col_w * i + col_w // 2
        svg += f"""
  <text x="{cx}" y="{header_y + 50}" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['white']}" text-anchor="middle" letter-spacing="2">{ch.upper()}</text>
"""

    # Row data
    transports = [
        ("stdio", "teal",
         "Local subprocess",
         "command, args, env",
         "env-var inheritance",
         "Local tools.  CLI you trust."),
        ("SSE",   "slate",
         "Remote stream",
         "type, url, headers",
         "Authorization: Bearer",
         "Vendor.  Deprecating soon."),
        ("HTTP",  "gold",
         "Remote request",
         "type, url, headers",
         "X-API-Key  /  Bearer",
         "Vendor.  Modern default."),
    ]

    for ri, (name, color, network, keys, auth, when) in enumerate(transports):
        y = header_y + 80 + ri * row_h
        # Zebra band
        bg = "white" if ri % 2 == 0 else "cream"
        svg += f"""
  <rect x="{start_x}" y="{y}" width="{label_col_w + col_w * 4}" height="{row_h}" fill="{P[bg]}"/>
"""
        # Transport label cell
        svg += f"""
  <rect x="{start_x}" y="{y}" width="{label_col_w}" height="{row_h}" fill="{P[color]}" opacity="0.18"/>
  <rect x="{start_x}" y="{y}" width="14" height="{row_h}" fill="{P[color]}"/>
  <text x="{start_x + label_col_w//2}" y="{y + row_h//2 + 12}" font-family="{FONT_MONO}" font-size="34" font-weight="700"
        fill="{P['ink']}" text-anchor="middle">{name}</text>
"""
        # Data cells
        for ci, val in enumerate([network, keys, auth, when]):
            cx = start_x + label_col_w + col_w * ci + 30
            svg += f"""
  <text x="{cx}" y="{y + row_h//2 + 12}" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['ink']}">{val}</text>
"""

    # ENV var callout
    svg += f"""
  <rect x="60" y="945" width="1840" height="60" rx="8" fill="{P['gold']}" opacity="0.18"/>
  <rect x="60" y="945" width="14" height="60" fill="{P['gold']}"/>
  <text x="90" y="985" font-family="{FONT_STACK}" font-size="22" font-weight="600" fill="{P['ink']}">
    $&#123;ENV_VAR&#125; expansion works in env, args, AND headers across all three transports.  Commit the config.  Source the secret.
  </text>
"""

    svg += footer("Domain 2 - MCP Integration", "Segment 2")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 5. CLAUDE.md Hierarchy Stack
# ---------------------------------------------------------------------------

def claude_md_hierarchy() -> str:
    """Vertical stacked layers showing User -> Project -> Subtree -> Local."""
    P = PALETTE
    svg = svg_open()
    svg += title_band("CLAUDE.md hierarchy",
                      "Domain 3  -  User and project load every time.  Subtree loads on demand.")

    layers = [
        ("User",     "~/.claude/CLAUDE.md",      "Your machine, every project.  Personal defaults, voice rules, your stack preferences.",   "slate", "Always loads"),
        ("Project",  "./CLAUDE.md",              "Team conventions.  Checked into git.  Overrides user rules where they conflict.",         "teal",  "Always loads"),
        ("Subtree",  "./&lt;subdir&gt;/CLAUDE.md", "Frontend rules, infra rules.  Loads ONLY when the agent reads files in that subdirectory.","gold",  "On-demand load"),
        ("Local",    "./CLAUDE.local.md",        "Gitignored personal override.  Repo-specific tweaks that should not pollute team conventions.", "warm",  "Always loads (if present)"),
    ]

    band_h = 165
    start_y = 180
    box_x = 160
    box_w = 1600

    for i, (name, path, descr, color, load_rule) in enumerate(layers):
        y = start_y + i * band_h
        svg += f"""
  <rect x="{box_x}" y="{y}" width="{box_w}" height="{band_h - 18}" rx="12" fill="{P['white']}" stroke="{P[color]}" stroke-width="3"/>
  <rect x="{box_x}" y="{y}" width="22" height="{band_h - 18}" fill="{P[color]}"/>
  <text x="{box_x + 50}" y="{y + 50}" font-family="{FONT_STACK}" font-size="32" font-weight="700" fill="{P[color]}">{name}</text>
  <text x="{box_x + 250}" y="{y + 50}" font-family="{FONT_MONO}" font-size="26" font-weight="600" fill="{P['ink']}">{path}</text>
  <text x="{box_x + 50}" y="{y + 95}" font-family="{FONT_STACK}" font-size="20" font-weight="400" fill="{P['ink']}">{descr}</text>
  <text x="{box_x + 50}" y="{y + 128}" font-family="{FONT_STACK}" font-size="18" font-weight="600" fill="{P['mist']}" letter-spacing="2">{load_rule.upper()}</text>
"""

    # Add a load-order arrow on the left, OUTSIDE the card column.
    # Cards start at x=160; arrow stays at x=60 with a 70-px gap.
    svg += f"""
  <text x="60" y="195" font-family="{FONT_STACK}" font-size="18" font-weight="700"
        fill="{P['mist']}" letter-spacing="2">LOAD</text>
  <text x="60" y="218" font-family="{FONT_STACK}" font-size="18" font-weight="700"
        fill="{P['mist']}" letter-spacing="2">ORDER</text>
  <path d="M 90 240 L 90 855 M 80 845 L 90 860 L 100 845" stroke="{P['mist']}" stroke-width="3" fill="none"/>
"""

    svg += f"""
  <rect x="160" y="945" width="1600" height="56" rx="8" fill="{P['navy']}" opacity="0.08"/>
  <text x="180" y="980" font-family="{FONT_STACK}" font-size="22" font-weight="500" fill="{P['ink']}">
    Agent SDK:  settingSources = ["user", "project"] loads both.  Skill triggers and slash commands inherit from the same tree.
  </text>
"""

    svg += footer("Domain 3 - Claude Code Configuration (20%)", "Segment 2")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 6. Forced-Tool-Choice + Retry Flow
# ---------------------------------------------------------------------------

def forced_tool_choice() -> str:
    """Top-down flowchart showing Pydantic -> schema -> forced call -> validate -> retry."""
    P = PALETTE
    svg = svg_open()
    svg += title_band("Forced tool_choice = guaranteed JSON shape",
                      "Domain 4  -  The structured-output cheat code, with one retry guard")

    # Boxes (top to bottom)
    cx = 960
    boxes = [
        ("Define Pydantic model",        "class Invoice(BaseModel): ...",                                                   "slate", 175,  10),
        ("Convert to JSON Schema",       "Invoice.model_json_schema()  -  Pydantic gives this for free",                    "slate", 295,  10),
        ("Register as a tool",           "{ \"name\": \"extract_invoice\", \"input_schema\": &lt;schema&gt; }",            "teal",  415,  10),
        ("Force the call",               "tool_choice = { \"type\": \"tool\", \"name\": \"extract_invoice\" }",             "gold",  535,  10),
        ("Receive tool_use block",       "block.input is a dict matching your schema.  No json.loads, no fence-stripping.", "teal",  655,  10),
    ]

    box_w = 1100
    box_h = 96
    for title, sub, color, y, extra_w in boxes:
        x = cx - (box_w + extra_w) // 2
        svg += f"""
  <rect x="{x}" y="{y}" width="{box_w + extra_w}" height="{box_h}" rx="10" fill="{P['white']}" stroke="{P[color]}" stroke-width="3"/>
  <rect x="{x}" y="{y}" width="18" height="{box_h}" fill="{P[color]}"/>
  <text x="{x + 38}" y="{y + 38}" font-family="{FONT_STACK}" font-size="26" font-weight="700" fill="{P['ink']}">{title}</text>
  <text x="{x + 38}" y="{y + 76}" font-family="{FONT_MONO}" font-size="20" font-weight="400" fill="{P['mist']}">{sub}</text>
"""
        # Arrow down
        if y < 655:
            svg += f"""
  <path d="M {cx} {y + box_h + 2} L {cx} {y + box_h + 16} M {cx - 8} {y + box_h + 10} L {cx} {y + box_h + 18} L {cx + 8} {y + box_h + 10}"
        stroke="{P['mist']}" stroke-width="3" fill="none"/>
"""

    # Validation diamond
    diamond_cx, diamond_cy = cx, 820
    svg += f"""
  <path d="M {diamond_cx} 770 L {diamond_cx + 200} {diamond_cy} L {diamond_cx} {diamond_cy + 50} L {diamond_cx - 200} {diamond_cy} Z"
        fill="{P['navy']}"/>
  <text x="{diamond_cx}" y="{diamond_cy - 4}" font-family="{FONT_STACK}" font-size="22" font-weight="700"
        fill="{P['white']}" text-anchor="middle">Invoice(**block.input)</text>
  <text x="{diamond_cx}" y="{diamond_cy + 24}" font-family="{FONT_STACK}" font-size="20" font-weight="400"
        fill="{P['gold']}" text-anchor="middle">validates?</text>
"""
    # Connect last box to diamond
    svg += f"""
  <path d="M {cx} {655 + 96 + 2} L {cx} 768 M {cx - 8} 760 L {cx} 770 L {cx + 8} 760"
        stroke="{P['mist']}" stroke-width="3" fill="none"/>
"""

    # YES branch (left) - typed object
    svg += f"""
  <path d="M {diamond_cx - 200} {diamond_cy} L 250 {diamond_cy}" stroke="{P['teal']}" stroke-width="3" fill="none"/>
  <text x="{diamond_cx - 220}" y="{diamond_cy - 12}" font-family="{FONT_STACK}" font-size="22" font-weight="700" fill="{P['teal']}" text-anchor="end">YES</text>
  <rect x="90" y="{diamond_cy - 50}" width="320" height="100" rx="10" fill="{P['teal']}"/>
  <text x="250" y="{diamond_cy - 6}" font-family="{FONT_STACK}" font-size="28" font-weight="700" fill="{P['white']}" text-anchor="middle">Typed object</text>
  <text x="250" y="{diamond_cy + 24}" font-family="{FONT_STACK}" font-size="20" font-weight="400" fill="{P['ice']}" text-anchor="middle">ship it</text>
"""

    # NO branch (right) - retry once
    svg += f"""
  <path d="M {diamond_cx + 200} {diamond_cy} L 1670 {diamond_cy}" stroke="{P['warm']}" stroke-width="3" fill="none"/>
  <text x="{diamond_cx + 220}" y="{diamond_cy - 12}" font-family="{FONT_STACK}" font-size="22" font-weight="700" fill="{P['warm']}" text-anchor="end">NO</text>
  <rect x="1510" y="{diamond_cy - 50}" width="320" height="100" rx="10" fill="{P['warm']}"/>
  <text x="1670" y="{diamond_cy - 6}" font-family="{FONT_STACK}" font-size="28" font-weight="700" fill="{P['white']}" text-anchor="middle">Retry once</text>
  <text x="1670" y="{diamond_cy + 24}" font-family="{FONT_STACK}" font-size="20" font-weight="400" fill="{P['cream']}" text-anchor="middle">max_retries = 1</text>
"""

    # Retry loop arrow up
    svg += f"""
  <path d="M 1670 {diamond_cy - 50} C 1670 580, 1670 480, {cx + (box_w + 10)//2 + 20} 480 L {cx + (box_w + 10)//2 + 20} 510"
        stroke="{P['warm']}" stroke-width="3" fill="none" stroke-dasharray="6,6"/>
  <path d="M {cx + (box_w + 10)//2 + 14} 502 L {cx + (box_w + 10)//2 + 22} 514 L {cx + (box_w + 10)//2 + 28} 500"
        stroke="{P['warm']}" stroke-width="3" fill="none"/>
  <text x="1830" y="450" font-family="{FONT_STACK}" font-size="18" font-weight="600" fill="{P['warm']}" letter-spacing="1" text-anchor="end">APPEND ERROR AS TOOL_RESULT</text>
"""

    svg += footer("Domain 4 - Prompts and Structured Output (20%)", "Segment 3")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 7. Escalation Decision Tree
# ---------------------------------------------------------------------------

def escalation_tree() -> str:
    """Decision tree: customer signal -> escalate / continue."""
    P = PALETTE
    svg = svg_open()
    svg += title_band("Escalation triggers:  policy, complexity, risk, explicit request",
                      "Domain 5  -  Sentiment alone is not a routing signal")

    # Top: trigger
    svg += f"""
  <rect x="710" y="180" width="500" height="80" rx="10" fill="{P['navy']}"/>
  <text x="960" y="218" font-family="{FONT_STACK}" font-size="26" font-weight="700"
        fill="{P['white']}" text-anchor="middle">Customer signal arrives</text>
  <text x="960" y="248" font-family="{FONT_STACK}" font-size="20" font-weight="400"
        fill="{P['gold']}" text-anchor="middle">What kind?</text>
"""
    # Connect down
    svg += f"""
  <path d="M 960 262 L 960 295 M 952 287 L 960 297 L 968 287" stroke="{P['mist']}" stroke-width="3" fill="none"/>
"""

    # Four ESCALATE conditions (left set)
    escalate_conds = [
        ('Explicit human request',  '"I want a human NOW."  Do not clarify.  Do not try one more tool.'),
        ('Policy violation',         'Refund > $500, account closure, refund-on-non-customer.  Application-layer block.'),
        ('Complexity',               'Multi-system failure, cross-account, security incident.  One agent cannot own this.'),
        ('Risk / compliance',        'PII exposure, audit-flagged action, regulated workflow.  Human signs the audit log.'),
    ]
    box_w = 720
    box_h = 110
    gap = 16
    for i, (cond, detail) in enumerate(escalate_conds):
        y = 320 + i * (box_h + gap)
        svg += f"""
  <rect x="90" y="{y}" width="{box_w}" height="{box_h}" rx="10" fill="{P['white']}" stroke="{P['warm']}" stroke-width="3"/>
  <rect x="90" y="{y}" width="18" height="{box_h}" fill="{P['warm']}"/>
  <text x="120" y="{y + 42}" font-family="{FONT_STACK}" font-size="26" font-weight="700" fill="{P['ink']}">{cond}</text>
  <text x="120" y="{y + 78}" font-family="{FONT_STACK}" font-size="20" font-weight="400" fill="{P['mist']}">{detail}</text>
"""

    # ESCALATE label band
    svg += f"""
  <rect x="90" y="830" width="{box_w}" height="80" rx="10" fill="{P['warm']}"/>
  <text x="450" y="880" font-family="{FONT_STACK}" font-size="34" font-weight="700"
        fill="{P['white']}" text-anchor="middle" letter-spacing="3">ESCALATE</text>
"""

    # Right side: NOT escalation triggers (sentiment + frustration)
    not_conds = [
        ('Frustration  ("ugh, this is the worst")',  'Acknowledge it.  Resolve the underlying issue.  Frustration is not complexity.'),
        ('Length of conversation',                   'A 40-turn thread on a $5 refund is still a $5 refund.  Solve, do not punt.'),
        ('Negative sentiment alone',                 'Calm user with a multi-account dispute escalates.  Angry user with a PIN reset does not.'),
        ('Repeat contacts in a week',                'Investigate the root cause.  Escalation does not fix recurring failure modes.'),
    ]
    right_x = 1110
    for i, (cond, detail) in enumerate(not_conds):
        y = 320 + i * (box_h + gap)
        svg += f"""
  <rect x="{right_x}" y="{y}" width="{box_w}" height="{box_h}" rx="10" fill="{P['white']}" stroke="{P['teal']}" stroke-width="3"/>
  <rect x="{right_x}" y="{y}" width="18" height="{box_h}" fill="{P['teal']}"/>
  <text x="{right_x + 30}" y="{y + 42}" font-family="{FONT_STACK}" font-size="26" font-weight="700" fill="{P['ink']}">{cond}</text>
  <text x="{right_x + 30}" y="{y + 78}" font-family="{FONT_STACK}" font-size="20" font-weight="400" fill="{P['mist']}">{detail}</text>
"""

    # CONTINUE label band
    svg += f"""
  <rect x="{right_x}" y="830" width="{box_w}" height="80" rx="10" fill="{P['teal']}"/>
  <text x="{right_x + box_w//2}" y="880" font-family="{FONT_STACK}" font-size="34" font-weight="700"
        fill="{P['white']}" text-anchor="middle" letter-spacing="3">CONTINUE  -  RESOLVE</text>
"""

    # Header sub-bands - "If ANY of these..."
    svg += f"""
  <text x="450" y="305" font-family="{FONT_STACK}" font-size="20" font-weight="700"
        fill="{P['warm']}" text-anchor="middle" letter-spacing="3">IF ANY OF THESE  -  ESCALATE</text>
  <text x="{right_x + box_w//2}" y="305" font-family="{FONT_STACK}" font-size="20" font-weight="700"
        fill="{P['teal']}" text-anchor="middle" letter-spacing="3">NONE OF THESE ARE ESCALATION SIGNALS</text>
"""

    # Bottom callout: structured summary
    svg += f"""
  <rect x="90" y="940" width="1740" height="68" rx="8" fill="{P['gold']}" opacity="0.18"/>
  <rect x="90" y="940" width="18" height="68" fill="{P['gold']}"/>
  <text x="120" y="975" font-family="{FONT_STACK}" font-size="22" font-weight="600" fill="{P['ink']}">
    On escalation:  pass a STRUCTURED summary to the human queue.  Not the transcript.  Who, what, what was tried, what is blocked.
  </text>
"""

    svg += footer("Domain 5 - Context and Reliability (15%)", "Segment 3")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# 8. CCA-F Domain Weights Radial + Notebook Crosswalk
# ---------------------------------------------------------------------------

def cca_f_weights() -> str:
    """Donut chart of domain weights + notebook crosswalk table."""
    P = PALETTE
    import math

    svg = svg_open()
    svg += title_band("CCA-F domain weights and notebook crosswalk",
                      "Segment 4  -  D1 + D3 + D4 = 67% of the exam")

    # Donut chart on the left
    cx, cy = 540, 590
    r_outer = 290
    r_inner = 175

    domains = [
        ("D1", "Agentic Architecture",      27, "gold"),
        ("D3", "Claude Code",                20, "teal"),
        ("D4", "Prompts + Structured Out.",  20, "slate"),
        ("D2", "Tool Design + MCP",          18, "warm"),
        ("D5", "Context + Reliability",      15, "mist"),
    ]

    total = sum(d[2] for d in domains)
    angle = -90.0  # start at top

    def polar(r, deg):
        rad = math.radians(deg)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    for code, name, weight, color in domains:
        sweep = 360.0 * weight / total
        a0 = angle
        a1 = angle + sweep
        large = 1 if sweep > 180 else 0
        x0o, y0o = polar(r_outer, a0)
        x1o, y1o = polar(r_outer, a1)
        x0i, y0i = polar(r_inner, a0)
        x1i, y1i = polar(r_inner, a1)
        path = (
            f"M {x0o} {y0o} "
            f"A {r_outer} {r_outer} 0 {large} 1 {x1o} {y1o} "
            f"L {x1i} {y1i} "
            f"A {r_inner} {r_inner} 0 {large} 0 {x0i} {y0i} Z"
        )
        svg += f'  <path d="{path}" fill="{P[color]}" stroke="{P["white"]}" stroke-width="3"/>\n'

        # Label inside slice
        mid = (a0 + a1) / 2
        lx, ly = polar((r_outer + r_inner) / 2, mid)
        svg += f"""
  <text x="{lx}" y="{ly - 4}" font-family="{FONT_STACK}" font-size="34" font-weight="700"
        fill="{P['white']}" text-anchor="middle">{code}</text>
  <text x="{lx}" y="{ly + 28}" font-family="{FONT_STACK}" font-size="22" font-weight="700"
        fill="{P['white']}" text-anchor="middle">{weight}%</text>
"""
        angle = a1

    # Center hole text
    svg += f"""
  <circle cx="{cx}" cy="{cy}" r="{r_inner - 6}" fill="{P['white']}"/>
  <text x="{cx}" y="{cy - 18}" font-family="{FONT_STACK}" font-size="28" font-weight="700"
        fill="{P['ink']}" text-anchor="middle">CCA-F</text>
  <text x="{cx}" y="{cy + 14}" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['mist']}" text-anchor="middle">60 questions</text>
  <text x="{cx}" y="{cy + 44}" font-family="{FONT_STACK}" font-size="22" font-weight="400"
        fill="{P['mist']}" text-anchor="middle">passing = 720</text>
"""

    # Right side: notebook crosswalk
    table_x = 920
    table_y = 200
    svg += f"""
  <rect x="{table_x}" y="{table_y}" width="940" height="60" fill="{P['navy']}"/>
  <text x="{table_x + 24}" y="{table_y + 40}" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['gold']}" letter-spacing="2">DOMAIN</text>
  <text x="{table_x + 220}" y="{table_y + 40}" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['white']}" letter-spacing="2">WHERE WE TAUGHT IT</text>
  <text x="{table_x + 660}" y="{table_y + 40}" font-family="{FONT_STACK}" font-size="22" font-weight="600"
        fill="{P['white']}" letter-spacing="2">PRIMARY NOTEBOOK</text>
"""

    rows = [
        ("D1  -  27%", "Segment 1",            "segment-1-customer-support-agent.ipynb", "gold"),
        ("D2  -  18%", "Segment 2  +  2.5",    "segment-2-tool-design-and-mcp.ipynb",    "warm"),
        ("D3  -  20%", "Segment 2",            "segment-2-tool-design-and-mcp.ipynb",    "teal"),
        ("D4  -  20%", "Segment 3",            "segment-3-invoice-extractor.ipynb",      "slate"),
        ("D5  -  15%", "Segment 3 + parts S1", "segment-3-invoice-extractor.ipynb",      "mist"),
    ]
    for i, (d, where, nb, color) in enumerate(rows):
        y = table_y + 80 + i * 100
        bg = "white" if i % 2 == 0 else "cream"
        svg += f"""
  <rect x="{table_x}" y="{y}" width="940" height="90" fill="{P[bg]}"/>
  <rect x="{table_x}" y="{y}" width="14" height="90" fill="{P[color]}"/>
  <text x="{table_x + 30}" y="{y + 55}" font-family="{FONT_STACK}" font-size="26" font-weight="700" fill="{P['ink']}">{d}</text>
  <text x="{table_x + 220}" y="{y + 55}" font-family="{FONT_STACK}" font-size="22" font-weight="400" fill="{P['ink']}">{where}</text>
  <text x="{table_x + 660}" y="{y + 55}" font-family="{FONT_MONO}" font-size="18" font-weight="400" fill="{P['mist']}">{nb}</text>
"""

    # Bottom callout: study weighting
    svg += f"""
  <rect x="60" y="945" width="1800" height="60" rx="8" fill="{P['gold']}" opacity="0.18"/>
  <rect x="60" y="945" width="18" height="60" fill="{P['gold']}"/>
  <text x="90" y="985" font-family="{FONT_STACK}" font-size="22" font-weight="600" fill="{P['ink']}">
    Weight your study time the way the exam weights its questions.  D1 is 27% of the score AND the biggest single lever in production.
  </text>
"""

    svg += footer("CCA-F Certification Capstone", "Segment 4")
    svg += "</svg>"
    return svg


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

OUT_DIR = Path(__file__).resolve().parent.parent.parent / "images" / "infographics"

INFOGRAPHICS = [
    ("01-agentic-loop",          agentic_loop),
    ("02-defense-in-depth",      defense_in_depth),
    ("03-three-tier-tools",      three_tier_tools),
    ("04-mcp-transports",        mcp_transports),
    ("05-claude-md-hierarchy",   claude_md_hierarchy),
    ("06-forced-tool-choice",    forced_tool_choice),
    ("07-escalation-tree",       escalation_tree),
    ("08-cca-f-weights",         cca_f_weights),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in INFOGRAPHICS:
        svg_text = fn()
        svg_path = OUT_DIR / f"{name}.svg"
        png_path = OUT_DIR / f"{name}.png"
        svg_path.write_text(svg_text, encoding="utf-8")
        cairosvg.svg2png(
            bytestring=svg_text.encode("utf-8"),
            write_to=str(png_path),
            output_width=3840,
            output_height=2160,
        )
        size_kb = png_path.stat().st_size // 1024
        print(f"  {name}.png  ({size_kb} KB)")
    print(f"Wrote {len(INFOGRAPHICS)} infographics to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
