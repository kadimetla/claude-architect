"""Build the five teaching notebooks for Claude Architect Foundations.

Run this when notebook content changes. It writes .ipynb files into
``notebooks/`` with cleared outputs and no trailing metadata that would
diff noisily under git. The source-of-truth lives here in Python so the
notebooks are reviewable in PRs without nbdiff.

Usage:
    python scripts/build-notebooks.py            # builds all five
    python scripts/build-notebooks.py segment-1  # builds one by slug
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

REPO_ROOT = Path(__file__).resolve().parent.parent
NB_DIR = REPO_ROOT / "notebooks"

# Each notebook is a list of ("md" | "code", source) tuples.
# Builder functions live in their own modules under scripts/_notebooks/.
from _notebooks import (  # noqa: E402  (local module after path setup)
    segment_0_pre_flight,
    segment_1_customer_support,
    segment_2_tool_design,
    segment_2_5_control_surfaces,
    segment_3_invoice_extractor,
    segment_4_capstone,
)

BUILDERS = {
    "segment-0-pre-flight": segment_0_pre_flight.cells,
    "segment-1-customer-support-agent": segment_1_customer_support.cells,
    "segment-2-tool-design-and-mcp": segment_2_tool_design.cells,
    "segment-2-5-control-surfaces": segment_2_5_control_surfaces.cells,
    "segment-3-invoice-extractor": segment_3_invoice_extractor.cells,
    "segment-4-cca-f-capstone": segment_4_capstone.cells,
}


def _build_one(slug: str) -> Path:
    cells = BUILDERS[slug]()
    nb = new_notebook(metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    })
    for index, (kind, source) in enumerate(cells):
        # Deterministic cell IDs prevent phantom git diffs on rebuild.
        # Per nbformat spec, cell IDs are 1-64 chars, [a-zA-Z0-9_-].
        cell_id = hashlib.sha256(
            f"{slug}:{index}:{source}".encode("utf-8")
        ).hexdigest()[:16]
        if kind == "md":
            nb.cells.append(new_markdown_cell(source, id=cell_id))
        elif kind == "code":
            nb.cells.append(new_code_cell(source, id=cell_id))
        else:
            raise ValueError(f"unknown cell kind: {kind!r}")
    out = NB_DIR / f"{slug}.ipynb"
    nbformat.write(nb, out)
    return out


def main(argv: list[str]) -> int:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    NB_DIR.mkdir(exist_ok=True)
    targets = argv[1:] or list(BUILDERS.keys())
    unknown = [t for t in targets if t not in BUILDERS]
    if unknown:
        print(f"unknown notebook slug(s): {unknown}", file=sys.stderr)
        print(f"known: {list(BUILDERS.keys())}", file=sys.stderr)
        return 2
    for slug in targets:
        out = _build_one(slug)
        print(f"wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
