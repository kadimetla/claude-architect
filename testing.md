"""Coordinator-subagent pattern for multi-agent orchestration.

Hub-and-spoke: coordinator manages subagent communication,
context passing, and result aggregation.

CCA-F Domain 1, Task Statements 1.2 and 1.3

NOTE: Conceptual scaffold. The actual Agent SDK Task tool
is used in production implementations.
"""

# Key exam concepts:
#
# 1. Subagents have ISOLATED context. Pass findings explicitly.
# 2. Coordinator handles: decomposition, context, aggregation, errors
# 3. Parallel: emit multiple Task calls in one coordinator response
# 4. Scoped tools: each subagent gets ONLY its role's tools

#              [Coordinator]
#               /    |    \
#       [Search]  [Analyze]  [Synthesize]
#       (web)     (doc)      (verify_fact only)


SEARCH_AGENT = {
    "description": "Searches the web for information on a given topic",
    "allowed_tools": ["web_search", "fetch_url"],
}

ANALYSIS_AGENT = {
    "description": "Extracts structured findings from documents",
    "allowed_tools": ["read_document", "extract_data"],
}

SYNTHESIS_AGENT = {
    "description": "Combines findings into a cited report",
    # Scoped cross-role tool for simple fact checks only
    "allowed_tools": ["verify_fact"],
}
