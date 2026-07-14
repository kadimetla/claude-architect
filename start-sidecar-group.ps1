<#
.SYNOPSIS
    Bring the whole Claude Architect teaching stack up in one command.

.DESCRIPTION
    Opens the always-on sidecars for a live delivery, each in its own Windows
    Terminal tab so you can watch it, read its log, and Ctrl+C it independently:

      Tab  Jupyter     JupyterLab on the teaching notebooks (port 8888)
      Tab  Inspector   MCP Inspector against the FastMCP demo server (6274/6277)
      Tab  MCP CLI     The MCP client REPL, chatting through the demo server

    Runs preflight-class.ps1 first and refuses to launch anything if it fails.
    A half-started stack in front of a cohort is worse than no stack.

    IDEMPOTENT. Re-run it as many times as you like:
      - A sidecar whose port is already held is reported and SKIPPED, not
        duplicated and not killed. Re-running after one tab dies brings only
        that tab back.
      - Use -Restart to force every sidecar down and back up.
      - The underlying launchers own their own ports and clear Windows
        half-states, so a hard restart is safe.

    The MCP servers themselves need nothing started here. Claude Code reads
    .mcp.json and GitHub Copilot reads .vscode/mcp.json; both spawn their stdio
    servers on demand when the editor opens. Preflight verifies both files parse
    and agree on the demo server name, which is the failure that actually bites.

.PARAMETER Port
    JupyterLab port. Defaults to 8888.

.PARAMETER Restart
    Stop every sidecar first, then start them all fresh. Without this, running
    sidecars are left alone.

.PARAMETER SkipPreflight
    Launch without the go/no-go check. For when you already ran preflight and
    are just re-opening a tab you closed.

.PARAMETER NoMcpCli
    Skip the MCP CLI REPL tab. It is the only interactive sidecar and it burns
    tokens on every turn, so you may want it only when you are about to demo it.

.PARAMETER NoJupyter
    Skip the JupyterLab tab. Use this when you teach the notebooks from VS Code:
    the VS Code Jupyter extension starts its OWN kernel process and never talks
    to the JupyterLab server on 8888, so that sidecar is dead weight in that
    workflow. The kernel it picks comes from the interpreter, not from this
    server - see the kernel note in scripts/preflight-class.ps1.

.EXAMPLE
    .\start-sidecar-group.ps1
    Preflight, then open the three sidecar tabs. Safe to re-run.

.EXAMPLE
    .\start-sidecar-group.ps1 -Restart
    Tear down whatever is running and bring the full stack up clean.

.EXAMPLE
    .\start-sidecar-group.ps1 -NoMcpCli
    Jupyter and Inspector only. Add the CLI later by re-running without the flag.

.EXAMPLE
    .\start-sidecar-group.ps1 -NoJupyter
    The VS Code workflow: Inspector and MCP CLI only. You run the notebooks from
    the VS Code Jupyter extension, so no JupyterLab server is needed.

.NOTES
    Author: Tim Warner

    Why tabs and not background jobs? A background job hides its output. When a
    demo misbehaves live, the fastest recovery is reading the actual stack trace
    and hitting Ctrl+C in that one window. Tabs preserve both. If Windows
    Terminal (wt.exe) is not on PATH, this falls back to separate pwsh windows.

    To take it all down: .\stop-sidecar-group.ps1
#>
[CmdletBinding()]
param(
    [int]$Port = 8888,
    [switch]$Restart,
    [switch]$SkipPreflight,
    [switch]$NoMcpCli,
    [switch]$NoJupyter
)

$ErrorActionPreference = 'Stop'

$repoRoot   = $PSScriptRoot
$scriptsDir = Join-Path $repoRoot 'scripts'

# pwsh, not powershell. The 5.1 host is on the box and would silently win the
# name lookup, then choke on the PS7 syntax in these scripts.
$pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue)?.Source
if (-not $pwsh) {
    throw "PowerShell 7 (pwsh) is not on PATH. These scripts are PS7, not Windows PowerShell 5.1."
}

function Test-PortHeld {
    param([int]$P)
    [bool](Get-NetTCPConnection -LocalPort $P -State Listen -ErrorAction SilentlyContinue)
}

# A bound port is NOT proof the service is usable. An orphaned node process from
# a dead Inspector holds 6274/6277 forever, which made the old skip path report
# "already up" while there was no window to drive and no Inspector to look at.
# Same lesson as the wt.exe no-op: probe the real thing, not a proxy for it.
function Test-HttpAlive {
    param([string]$Url, [int]$TimeoutSec = 5)
    try {
        $r = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400)
    }
    catch { return $false }
}

# Free a port whose listener is not actually serving. Scoped to the exact port,
# so this can never take down an unrelated service on the box.
function Clear-StalePort {
    param([int]$P, [string]$Label)
    $conns = Get-NetTCPConnection -LocalPort $P -State Listen -ErrorAction SilentlyContinue
    foreach ($procId in ($conns | Select-Object -ExpandProperty OwningProcess -Unique)) {
        $name = (Get-Process -Id $procId -ErrorAction SilentlyContinue)?.ProcessName ?? 'unknown'
        Write-Warning "Port $P ($Label) held by a dead $name (PID $procId). Reclaiming it."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 750
}

# --- Preflight -------------------------------------------------------------
if (-not $SkipPreflight) {
    Write-Host 'Running preflight...' -ForegroundColor Cyan
    & (Join-Path $scriptsDir 'preflight-class.ps1') -Port $Port
    if ($LASTEXITCODE -ne 0) {
        Write-Host ''
        Write-Host 'Preflight failed. Nothing launched. Fix the FAIL rows above, then re-run.' -ForegroundColor Red
        exit 1
    }
}

# --- Restart path ----------------------------------------------------------
if ($Restart) {
    Write-Host ''
    Write-Host 'Restart requested. Stopping running sidecars...' -ForegroundColor Yellow
    & (Join-Path $repoRoot 'stop-sidecar-group.ps1') -Port $Port
    Write-Host ''
}

# --- Decide what actually needs launching ----------------------------------
# Port-held means "already up". Skipping is what makes re-running this script
# safe: it repairs the gaps instead of stacking duplicate servers.
$tabs = [System.Collections.Generic.List[object]]::new()

# The VS Code Jupyter extension spawns its own kernel and never connects to a
# JupyterLab server, so -NoJupyter is the correct flag for that workflow rather
# than an optimization. Nothing is stopped here: an already-running JupyterLab
# is left alone, because -NoJupyter means "do not start one", not "kill one".
if ($NoJupyter) {
    if (Test-PortHeld -P $Port) {
        Write-Host "Jupyter skipped (-NoJupyter). One is already up on $Port; leaving it alone." -ForegroundColor DarkGray
    }
    else {
        Write-Host 'Jupyter skipped (-NoJupyter). Run the notebooks from VS Code.' -ForegroundColor DarkGray
    }
}
elseif (Test-PortHeld -P $Port) {
    Write-Host "Jupyter already up on port $Port. Skipping." -ForegroundColor DarkGray
}
else {
    $tabs.Add([pscustomobject]@{
        Title   = 'Jupyter'
        Command = "& '$(Join-Path $scriptsDir 'run-jupyter.ps1')' -Port $Port"
    })
}

# Skip ONLY if the Inspector is genuinely reachable. A held port with no HTTP
# answer is an orphan from a prior run: it must be reclaimed, not respected.
$inspectorHeld = (Test-PortHeld -P 6274) -or (Test-PortHeld -P 6277)
$inspectorAlive = $inspectorHeld -and (Test-HttpAlive -Url 'http://localhost:6274')

if ($inspectorAlive) {
    Write-Host 'MCP Inspector already up and answering on http://localhost:6274. Skipping.' -ForegroundColor DarkGray
}
else {
    if ($inspectorHeld) {
        Write-Host 'MCP Inspector ports are held but nothing is serving. Reclaiming them.' -ForegroundColor Yellow
        Clear-StalePort -P 6274 -Label 'Inspector UI'
        Clear-StalePort -P 6277 -Label 'Inspector proxy'
    }
    $tabs.Add([pscustomobject]@{
        Title   = 'MCP Inspector'
        Command = "& '$(Join-Path $scriptsDir 'run-mcp-inspector.ps1')'"
    })
}

# The MCP CLI is a REPL with no port to probe, so there is no reliable way to
# detect a running one. Re-running without -Restart opens a second REPL tab.
# That is harmless (each is its own process talking to its own stdio server)
# but worth knowing, so say it out loud rather than pretending otherwise.
if (-not $NoMcpCli) {
    $tabs.Add([pscustomobject]@{
        Title   = 'MCP CLI'
        Command = "& '$(Join-Path $scriptsDir 'run-mcp-cli.ps1')'"
    })
}

if ($tabs.Count -eq 0) {
    Write-Host ''
    Write-Host 'Everything is already running. Nothing to do.' -ForegroundColor Green
    if (-not $NoJupyter) { Write-Host "  JupyterLab      http://localhost:$Port" }
    # Reaching here means the Inspector answered HTTP above, so this URL is a
    # verified claim, not a hopeful one.
    Write-Host '  MCP Inspector   http://localhost:6274  (verified answering)'
    Write-Host ''
    Write-Host 'No Inspector window in front of you? It is running headless from an'
    Write-Host 'earlier launch. Re-run with -Restart to get a window you can Ctrl+C.'
    exit 0
}

# --- Launch ----------------------------------------------------------------
# Two launch strategies, and we do NOT trust either one blindly.
#
# `wt.exe` on PATH is usually the Store execution alias under WindowsApps - a
# zero-byte reparse point, not a real binary. Launched from an interactive
# session it opens tabs correctly; launched from some non-interactive or
# sandboxed hosts it silently no-ops and Start-Process still "succeeds".
#
# So: try wt, then VERIFY the ports actually came up, and fall back to plain
# pwsh windows if they did not. A launcher that reports success without
# confirming the service is listening is a launcher that lies to you live.
$wt = (Get-Command wt -ErrorAction SilentlyContinue)?.Source

Write-Host ''
Write-Host ("Launching {0} sidecar(s): {1}" -f $tabs.Count, (($tabs.Title) -join ', ')) -ForegroundColor Cyan

function Start-InPlainWindows {
    param([object[]]$Tabs)
    foreach ($tab in $Tabs) {
        Start-Process -FilePath $pwsh `
            -ArgumentList @('-NoExit', '-Command', $tab.Command) `
            -WorkingDirectory $repoRoot | Out-Null
    }
}

if ($wt) {
    # One `wt` invocation with `;` separators opens all tabs in a single window.
    # Launching them one at a time would scatter them across several windows.
    $wtArgs = [System.Collections.Generic.List[string]]::new()
    foreach ($tab in $tabs) {
        if ($wtArgs.Count -gt 0) { $wtArgs.Add(';') }
        $wtArgs.Add('new-tab')
        $wtArgs.Add('--title');             $wtArgs.Add($tab.Title)
        $wtArgs.Add('--startingDirectory'); $wtArgs.Add($repoRoot)
        $wtArgs.Add($pwsh)
        # -NoExit keeps the tab alive after the sidecar stops, so a crash leaves
        # its stack trace on screen instead of vanishing the window.
        $wtArgs.Add('-NoExit')
        $wtArgs.Add('-Command'); $wtArgs.Add($tab.Command)
    }
    Start-Process -FilePath $wt -ArgumentList $wtArgs | Out-Null
}
else {
    Write-Warning 'Windows Terminal (wt.exe) not found. Using separate pwsh windows.'
    Start-InPlainWindows -Tabs $tabs
}

# --- Verify ----------------------------------------------------------------
# Only the port-backed sidecars can be probed. Jupyter and the Inspector both
# bind ports; the MCP CLI is a REPL with nothing to listen on, so it is launched
# but not asserted.
#
# Where a sidecar serves HTTP, the bound port is the WEAK signal and the HTTP
# answer is the strong one. The Inspector is the case that matters: `mcp dev`
# binds the proxy (6277) seconds before the Vite UI (6274) starts serving, so
# waiting on 6277 alone declares "up" while the page you actually open still
# refuses connections. Wait on the URL you are about to hand the room.
$expectPorts = [System.Collections.Generic.List[object]]::new()
if ($tabs.Title -contains 'Jupyter') {
    $expectPorts.Add(@{ N = $Port; Label = 'JupyterLab'; Url = $null })
}
if ($tabs.Title -contains 'MCP Inspector') {
    $expectPorts.Add(@{ N = 6274; Label = 'MCP Inspector'; Url = 'http://localhost:6274' })
}

# A sidecar is "up" when its port is bound AND, if it serves HTTP, it answers.
function Test-SidecarUp {
    param([hashtable]$Sidecar)
    if (-not (Test-PortHeld -P $Sidecar.N)) { return $false }
    if (-not $Sidecar.Url) { return $true }
    return (Test-HttpAlive -Url $Sidecar.Url -TimeoutSec 3)
}

if ($expectPorts.Count -gt 0) {
    Write-Host 'Waiting for sidecars to come up (port bound, and answering if HTTP)...' -ForegroundColor DarkGray

    # Cold start pulls a uv venv and an npx download on a clean box. 90s is
    # generous on purpose: a false "did not come up" that sends you chasing a
    # non-bug costs more than waiting.
    $deadline = (Get-Date).AddSeconds(90)
    $pending  = [System.Collections.Generic.List[object]]::new($expectPorts)

    while ((Get-Date) -lt $deadline -and $pending.Count -gt 0) {
        foreach ($p in @($pending)) {
            if (Test-SidecarUp -Sidecar $p) {
                Write-Host ("  UP    {0} (port {1})" -f $p.Label, $p.N) -ForegroundColor Green
                $pending.Remove($p) | Out-Null
            }
        }
        if ($pending.Count -gt 0) { Start-Sleep -Milliseconds 750 }
    }

    if ($pending.Count -gt 0 -and $wt) {
        # wt was on PATH but nothing came up. Near-certainly the Store-alias no-op,
        # which means NOTHING wt was asked to open actually opened - including the
        # portless MCP CLI, whose absence we cannot detect by probing. So relaunch
        # every tab, not just the pending port-backed ones. The Inspector's own
        # launcher reclaims its ports first, so a double-launch cannot collide.
        Write-Warning 'Windows Terminal did not open (Store execution alias no-op). Retrying in plain pwsh windows.'
        Start-InPlainWindows -Tabs $tabs

        $deadline = (Get-Date).AddSeconds(90)
        while ((Get-Date) -lt $deadline -and $pending.Count -gt 0) {
            foreach ($p in @($pending)) {
                if (Test-SidecarUp -Sidecar $p) {
                    Write-Host ("  UP    {0} (port {1})" -f $p.Label, $p.N) -ForegroundColor Green
                    $pending.Remove($p) | Out-Null
                }
            }
            if ($pending.Count -gt 0) { Start-Sleep -Milliseconds 750 }
        }
    }

    foreach ($p in $pending) {
        Write-Warning ("DOWN  {0} (port {1}) never came up. Read that sidecar's window for the error." -f $p.Label, $p.N)
    }

    if ($pending.Count -gt 0) {
        Write-Host ''
        Write-Host 'Some sidecars did not come up. Stack is PARTIAL.' -ForegroundColor Red
        exit 1
    }
}

Write-Host ''
Write-Host 'Sidecars up.' -ForegroundColor Green
if ($NoJupyter) {
    Write-Host '  JupyterLab      skipped - run the notebooks from VS Code'
}
else {
    Write-Host "  JupyterLab      http://localhost:$Port"
}
Write-Host '  MCP Inspector   http://localhost:6274  (opens automatically)'
if ($NoMcpCli) {
    # -NoMcpCli is easy to pass and easy to forget you passed. Say the exact
    # command to start it by hand rather than leaving you to go find it.
    Write-Host '  MCP CLI         SKIPPED (-NoMcpCli). Start it yourself with:' -ForegroundColor Yellow
    Write-Host '                    .\scripts\run-mcp-cli.ps1' -ForegroundColor Yellow
}
else {
    Write-Host '  MCP CLI         chat REPL in its own window'
}
Write-Host ''
Write-Host 'Teaching notebooks are in notebooks/ - five live-taught:'
Write-Host '  segment-0-pre-flight              env check, optional'
Write-Host '  segment-1-customer-support-agent  Domain 1'
Write-Host '  segment-2-tool-design-and-mcp     Domains 2 + 3'
Write-Host '  segment-3-invoice-extractor       Domains 4 + 5'
Write-Host '  segment-4-cca-f-capstone          cert briefing + questions'
Write-Host ''
Write-Host 'Take it all down with:  .\stop-sidecar-group.ps1'
