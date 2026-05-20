<#
.SYNOPSIS
    Start the Claude Architect teaching notebooks in JupyterLab.

.DESCRIPTION
    Launches JupyterLab through the notebooks uv project so the managed
    notebooks/.venv environment is used every time. The command also sets
    Jupyternaut as the default Jupyter AI persona; without that override,
    Jupyter AI v3 can load both Copilot and Jupyternaut but route messages to
    nobody.

.PARAMETER Port
    Port for JupyterLab. Defaults to 8888.

.EXAMPLE
    .\scripts\run-jupyter.ps1
    Starts JupyterLab for the teaching notebooks on port 8888.

.EXAMPLE
    .\scripts\run-jupyter.ps1 -Port 8890
    Starts JupyterLab on port 8890.
#>
[CmdletBinding()]
param(
    [int]$Port = 8888
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$notebooksDir = Join-Path $repoRoot 'notebooks'

if (-not (Test-Path -LiteralPath $notebooksDir -PathType Container)) {
    throw "Notebooks directory not found at $notebooksDir. Was notebooks/ deleted?"
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not on PATH. Install with 'winget install astral-sh.uv' or 'pip install uv', then re-run."
}

# Jupyter AI v3 installs Jupyternaut under jupyter_ai_jupyternaut. The upstream
# default persona ID still points at the older jupyter_ai package ID, which
# leaves chat messages with no default responder.
$personaId = 'jupyter-ai-personas::jupyter_ai_jupyternaut::JupyternautPersona'

& uv run --project $notebooksDir jupyter lab $notebooksDir `
    --port $Port `
    --PersonaManager.default_persona_id="$personaId"

exit $LASTEXITCODE
