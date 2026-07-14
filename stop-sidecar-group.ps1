<#
.SYNOPSIS
    Take the Claude Architect teaching sidecars back down.

.DESCRIPTION
    The counterpart to start-sidecar-group.ps1. Stops, in order:

      Jupyter     via scripts/stop-jupyter.ps1 (graceful, with exact-PID fallback)
      Inspector   by freeing ports 6274 and 6277
      Windows     the -NoExit sidecar windows those servers were launched from
      Orphans     any MCP stdio server left behind by a killed window

    IDEMPOTENT. Stopping something that is already stopped is a no-op that
    reports and moves on, never an error.

    Leaves exactly one terminal standing: yours.

.PARAMETER Port
    JupyterLab port to stop. Defaults to 8888.

.EXAMPLE
    .\stop-sidecar-group.ps1
    Full teardown. Your own shell survives; every sidecar window does not.

.NOTES
    Author: Tim Warner

    Scoped by design, two different ways.

    Servers are port-scoped: every stop targets a specific port or a PID resolved
    from that port, so this can never take down an unrelated Jupyter or Node
    service on the box.

    Windows are cmdline-scoped: a sidecar window carries run-mcp-cli.ps1 or
    run-mcp-inspector.ps1 literally in its command line, and an instructor's shell
    does not. This file used to refuse to close the REPL at all, on the grounds
    that pattern-matching pwsh is how you close the window you are teaching from.
    That was the right fear aimed at the wrong discriminator: `pwsh` is a guess,
    the launcher filename is exact. Both sweeps additionally skip this process and
    every one of its ancestors, because a sweep that matches on command-line text
    will otherwise match the shell running the sweep.
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

# --- Sidecar windows -------------------------------------------------------
# Freeing the ports kills the SERVER but not the window that launched it. Those
# windows are started with -NoExit (on purpose: a crash must leave its stack
# trace on screen), so every relaunch strands another dead husk. Left alone,
# a teaching day accumulates a dozen of them.
#
# The old note here said "killing every pwsh that looks like a REPL is how you
# close the window you are teaching from". Correct, and worth keeping. But
# `pwsh` was never the right discriminator. The sidecar windows carry the
# launcher script's own filename in their command line; an instructor's shell
# never does. That string is exact, not a heuristic.
#
# Two guard rails, both load-bearing:
#   1. Require run-mcp-cli.ps1 / run-mcp-inspector.ps1 literally in the cmdline.
#   2. Never touch this process or any of its ancestors. A sweep that matches on
#      command-line text WILL match the shell running the sweep. Ask me how I know.
function Get-SelfAncestry {
    $chain = [System.Collections.Generic.List[int]]::new()
    $chain.Add($PID)
    $p = Get-CimInstance Win32_Process -Filter "ProcessId=$PID" -ErrorAction SilentlyContinue
    while ($p -and $p.ParentProcessId -and $p.ParentProcessId -ne 0) {
        $chain.Add([int]$p.ParentProcessId)
        $p = Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue
    }
    return $chain
}

function Stop-SidecarWindows {
    $self = Get-SelfAncestry

    $windows = Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -match 'run-mcp-cli\.ps1|run-mcp-inspector\.ps1' -and
            $_.ProcessId -notin $self
        }

    if (-not $windows) {
        Write-Host 'No sidecar windows to close.'
        return
    }

    foreach ($w in $windows) {
        $label = if ($w.CommandLine -match 'run-mcp-cli') { 'MCP CLI' } else { 'MCP Inspector' }
        Write-Host "Closing $label window (PID $($w.ProcessId))."
        Stop-Process -Id $w.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

Stop-SidecarWindows

# The REPL's stdio server is a child of the REPL, so closing the window above
# normally reaps it. Normally. When a window was killed out from under it, the
# uv -> python -> python chain survives as an orphan holding nothing, invisible
# because it has no port to probe. Sweep those too, under the same guard rails.
function Stop-OrphanedMcpServers {
    $self = Get-SelfAncestry

    $orphans = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -match 'mcp_server\.py|mcp_cli' -and
            $_.Name -in @('python.exe', 'uv.exe') -and
            $_.ProcessId -notin $self
        }

    if (-not $orphans) {
        Write-Host 'No orphaned MCP stdio servers.'
        return
    }

    foreach ($o in $orphans) {
        Stop-Process -Id $o.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Reaped $(@($orphans).Count) orphaned MCP stdio process(es)."
}

Stop-OrphanedMcpServers

Write-Host ''
Write-Host 'Sidecars down.' -ForegroundColor Green
