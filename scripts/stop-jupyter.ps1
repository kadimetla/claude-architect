<#
.SYNOPSIS
    Stop the Claude Architect JupyterLab server started from notebooks/.

.DESCRIPTION
    Uses Jupyter's own server registry to find a running notebook server for
    this repo, asks it to shut down through `jupyter server stop`, then verifies
    that the process exited. If Jupyter's shutdown route hangs, the script stops
    only the matching server PID from the runtime file.

    Why the fallback exists: Jupyter AI / Jupyternaut can leave the server in a
    half-interrupted state on Windows. Repeated Ctrl+C can print "Interrupted..."
    without letting the event loop finish shutdown.

.PARAMETER Port
    Jupyter server port to stop. Defaults to 8888.

.PARAMETER TimeoutSeconds
    Seconds to wait after the graceful stop request before using the exact-PID
    fallback. Defaults to 10.

.EXAMPLE
    .\scripts\stop-jupyter.ps1
    Stops the notebooks JupyterLab server on port 8888.

.EXAMPLE
    .\scripts\stop-jupyter.ps1 -Port 8890
    Stops the notebooks JupyterLab server on port 8890.
#>
[CmdletBinding()]
param(
    [int]$Port = 8888,
    [int]$TimeoutSeconds = 10
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$notebooksRoot = Join-Path $repoRoot 'notebooks'

if (-not (Test-Path -LiteralPath $notebooksRoot -PathType Container)) {
    throw "Notebooks directory not found at $notebooksRoot. Was notebooks/ deleted?"
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not on PATH. Install uv or run this from a shell where uv is available."
}

$runtimeDir = (& uv run --project $notebooksRoot jupyter --runtime-dir 2>$null).Trim()
if (-not $runtimeDir) {
    $runtimeDir = Join-Path $env:APPDATA 'jupyter\runtime'
}

function Get-NotebookServerRuntime {
    if (-not (Test-Path $runtimeDir)) {
        return $null
    }

    Get-ChildItem -LiteralPath $runtimeDir -Filter 'jpserver-*.json' -Force |
        ForEach-Object {
            try {
                Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
            }
            catch {
                Write-Warning "Could not read Jupyter runtime file $($_.FullName): $($_.Exception.Message)"
                $null
            }
        } |
        Where-Object {
            $_ -and
            $_.port -eq $Port -and
            ([System.IO.Path]::GetFullPath($_.root_dir).TrimEnd('\') -ieq
                [System.IO.Path]::GetFullPath($notebooksRoot).TrimEnd('\'))
        } |
        Select-Object -First 1
}

$server = Get-NotebookServerRuntime
if (-not $server) {
    Write-Host "No notebooks Jupyter server found on port $Port."
    exit 0
}

Write-Host "Stopping Jupyter server on port $Port (PID $($server.pid))..."

$stdoutPath = Join-Path ([System.IO.Path]::GetTempPath()) "claude-architect-jupyter-stop-$Port.out"
$stderrPath = Join-Path ([System.IO.Path]::GetTempPath()) "claude-architect-jupyter-stop-$Port.err"
Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue

$stop = Start-Process -FilePath 'uv' `
    -ArgumentList @('run', '--project', $notebooksRoot, 'jupyter', 'server', 'stop', "$Port") `
    -WorkingDirectory $repoRoot `
    -PassThru `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    if (-not (Get-Process -Id $server.pid -ErrorAction SilentlyContinue)) {
        Write-Host "Jupyter server stopped cleanly."
        Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
        exit 0
    }
    if ($stop.HasExited) {
        break
    }
    Start-Sleep -Milliseconds 500
}

if (-not $stop.HasExited) {
    Stop-Process -Id $stop.Id -Force -ErrorAction SilentlyContinue
}

$stillRunning = Get-Process -Id $server.pid -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Warning "Jupyter did not exit after the graceful stop request. Stopping exact PID $($server.pid)."
    Stop-Process -Id $server.pid -Force
    Write-Host "Stopped stuck Jupyter server process."
}
else {
    Write-Host "Jupyter server stopped cleanly."
}

Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
