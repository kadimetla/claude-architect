<#
.SYNOPSIS
    Take the Claude Architect teaching sidecars back down.

.DESCRIPTION
    The counterpart to start-sidecar-group.ps1. Stops, in order:

      Jupyter     via scripts/stop-jupyter.ps1 (graceful, with exact-PID fallback)
      Inspector   by freeing ports 6274 and 6277

    IDEMPOTENT. Stopping something that is already stopped is a no-op that
    reports and moves on, never an error.

    The MCP CLI REPL is NOT stopped here. It is an interactive foreground
    process in its own tab with no port to identify it, and killing every pwsh
    that looks like it could be a REPL is how you accidentally close the window
    you are teaching from. Close that tab yourself, or type its quit command.

.PARAMETER Port
    JupyterLab port to stop. Defaults to 8888.

.EXAMPLE
    .\stop-sidecar-group.ps1
    Stops Jupyter and the MCP Inspector. Leaves the MCP CLI tab alone.

.NOTES
    Author: Tim Warner

    Port-scoped by design. Every stop here targets a specific port or a specific
    PID resolved from that port, so this can never take down an unrelated Jupyter
    or Node service running elsewhere on the box.
#>
[CmdletBinding()]
param(
    [int]$Port = 8888
)

$ErrorActionPreference = 'Stop'

$repoRoot   = $PSScriptRoot
$scriptsDir = Join-Path $repoRoot 'scripts'

Write-Host 'Stopping Claude Architect sidecars...' -ForegroundColor Cyan

# --- Jupyter ---------------------------------------------------------------
# Delegate to the existing script. It matches the server by root_dir, so it only
# ever stops the notebooks server and not some other Jupyter on the box.
$stopJupyter = Join-Path $scriptsDir 'stop-jupyter.ps1'
if (Test-Path -LiteralPath $stopJupyter -PathType Leaf) {
    try {
        & $stopJupyter -Port $Port
    }
    catch {
        Write-Warning "stop-jupyter.ps1 reported: $($_.Exception.Message)"
    }
}
else {
    Write-Warning "Not found: $stopJupyter"
}

# --- MCP Inspector ---------------------------------------------------------
# `mcp dev` spawns npx -> node. Ctrl+C in the tab does not always reap the child,
# which is exactly the orphaned-node-holds-6277 state that makes the next launch
# print PORT IS IN USE. Free the ports explicitly.
function Stop-Port {
    param([int]$P, [string]$Label)

    $conns = Get-NetTCPConnection -LocalPort $P -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "Port $P ($Label) already free."
        return
    }

    foreach ($procId in ($conns | Select-Object -ExpandProperty OwningProcess -Unique)) {
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        $name = if ($proc) { $proc.ProcessName } else { 'unknown' }
        Write-Host "Stopping PID $procId ($name) on port $P ($Label)."
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
        }
        catch {
            Write-Warning "Could not stop PID ${procId} on port ${P}: $($_.Exception.Message)"
        }
    }

    # Sockets sit in TIME_WAIT briefly after the owner dies.
    Start-Sleep -Milliseconds 750
    if (Get-NetTCPConnection -LocalPort $P -State Listen -ErrorAction SilentlyContinue) {
        Write-Warning "Port $P ($Label) is still held after the stop attempt."
    }
    else {
        Write-Host "Port $P ($Label) freed."
    }
}

Stop-Port -P 6274 -Label 'Inspector UI'
Stop-Port -P 6277 -Label 'Inspector proxy'

Write-Host ''
Write-Host 'Sidecars down.' -ForegroundColor Green
Write-Host 'The MCP CLI REPL, if open, is a foreground tab - close it yourself.'
