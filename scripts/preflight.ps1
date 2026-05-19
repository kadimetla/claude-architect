<#
.SYNOPSIS
    Pre-class preflight automation for the Claude Architect Foundations live training.

.DESCRIPTION
    Collapses the 35-checkbox PRE-CLASS-CHECKLIST.md into one non-interactive run.
    Checks environment versions, API auth, repo state, demo file presence, and
    .mcp.json validity. Exits non-zero on any failure so a red light is impossible
    to miss 30 minutes before going live.

    What this script CANNOT verify (still requires Tim's eyeballs):
      - Sample invoice fixtures for Segment 3 (no canonical location)
      - O'Reilly platform tab open, screen-share rehearsed
      - Phone silenced, coffee made
      - Claude Code MCP servers connected (requires running `claude mcp list` live)

.EXAMPLE
    pwsh ./scripts/preflight.ps1
    Runs every automated check and reports a pass/fail summary.

.EXAMPLE
    npm run preflight
    Same thing via npm script.

.NOTES
    Author: Tim Warner
    Run this 30 minutes before going live. If anything is red, fix it before
    students arrive. The cost of fixing a missing env var in front of 50 paying
    attendees is much higher than the 2 minutes this script takes.
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Continue'

$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Section,
        [string]$Name,
        [bool]$Pass,
        [string]$Detail = ''
    )
    $results.Add([pscustomobject]@{
        Section = $Section
        Name    = $Name
        Pass    = $Pass
        Detail  = $Detail
    }) | Out-Null
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    } catch { return $false }
}

# 1. Environment
$psOk = $PSVersionTable.PSVersion.Major -ge 7
Add-Check 'Environment' 'PowerShell 7+' $psOk "Found $($PSVersionTable.PSVersion)"

$pyVer = ''
if (Test-Command 'python') {
    $pyVer = (python --version 2>&1) -replace 'Python ', ''
}
$pyOk = $pyVer -match '^3\.(1[3-9]|[2-9]\d)'
Add-Check 'Environment' 'Python 3.13+' $pyOk "Found '$pyVer'"

$nodeVer = ''
if (Test-Command 'node') { $nodeVer = (node --version 2>&1) -replace '^v', '' }
$nodeOk = $nodeVer -match '^(1[89]|[2-9]\d)\.'
Add-Check 'Environment' 'Node 18+' $nodeOk "Found 'v$nodeVer'"

$claudeOk = Test-Command 'claude'
Add-Check 'Environment' 'Claude Code CLI on PATH' $claudeOk ''

# 2. API auth
$keyPresent = -not [string]::IsNullOrWhiteSpace($env:ANTHROPIC_API_KEY)
$keyLen = if ($keyPresent) { $env:ANTHROPIC_API_KEY.Length } else { 0 }
$keyOk = $keyPresent -and $keyLen -ge 90
Add-Check 'API auth' 'ANTHROPIC_API_KEY set (>= 90 chars)' $keyOk "Length: $keyLen"

# 3. Repo state
Push-Location $RepoRoot
try {
    $gitStatus = git status --porcelain 2>$null
    $gitClean = [string]::IsNullOrWhiteSpace($gitStatus)
    Add-Check 'Repo state' 'Working tree clean' $gitClean ''

    $branch = (git branch --show-current 2>$null).Trim()
    Add-Check 'Repo state' 'Branch is main' ($branch -eq 'main') "On '$branch'"
} finally { Pop-Location }

# 4. Demo file inventory
$demoFiles = @{
    'Segment 1 customer_service_agent.ipynb'  = 'claude-cookbooks-main/tool_use/customer_service_agent.ipynb'
    'Segment 1 hooks-example.py'              = 'hooks-example.py'
    'Segment 2 .mcp.json (repo root)'         = '.mcp.json'
    'Segment 2 CLAUDE.md (repo root)'         = 'CLAUDE.md'
    'Segment 3 extracting_structured_json'    = 'claude-cookbooks-main/tool_use/extracting_structured_json.ipynb'
    'Segment 3 tool_use_with_pydantic'        = 'claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb'
    'Segment 4 automatic-context-compaction'  = 'claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb'
}
foreach ($entry in $demoFiles.GetEnumerator()) {
    $full = Join-Path $RepoRoot $entry.Value
    Add-Check 'Demo files' $entry.Key (Test-Path $full) $entry.Value
}

# 5. .mcp.json validity
$mcpPath = Join-Path $RepoRoot '.mcp.json'
$mcpOk = $false
$mcpDetail = ''
if (Test-Path $mcpPath) {
    try {
        $mcp = Get-Content -LiteralPath $mcpPath -Raw | ConvertFrom-Json
        $serverCount = ($mcp.mcpServers.PSObject.Properties | Measure-Object).Count
        $mcpOk = $serverCount -gt 0
        $mcpDetail = "$serverCount server(s) defined"
    } catch {
        $mcpDetail = "Parse error: $($_.Exception.Message)"
    }
} else {
    $mcpDetail = 'File not found'
}
Add-Check '.mcp.json' 'Parses with >= 1 server' $mcpOk $mcpDetail

# 6. Python notebook deps smoke test
$importOk = $false
$importDetail = ''
if ($pyOk) {
    $out = python -c "import anthropic; print(anthropic.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $importOk = $true
        $importDetail = "anthropic SDK $($out.Trim())"
    } else {
        $importDetail = "anthropic import failed: $out"
    }
} else {
    $importDetail = 'Skipped (Python version check failed)'
}
Add-Check 'Notebook deps' 'anthropic SDK importable' $importOk $importDetail

# Report
$total = $results.Count
$passed = ($results | Where-Object Pass).Count
$failed = $total - $passed

Write-Host ''
Write-Host '== PREFLIGHT REPORT ==' -ForegroundColor Cyan
$results | Group-Object Section | ForEach-Object {
    Write-Host ''
    Write-Host "[$($_.Name)]" -ForegroundColor Cyan
    foreach ($r in $_.Group) {
        $mark = if ($r.Pass) { '[OK]' } else { '[FAIL]' }
        $color = if ($r.Pass) { 'Green' } else { 'Red' }
        $detail = if ($r.Detail) { " - $($r.Detail)" } else { '' }
        Write-Host "  $mark $($r.Name)$detail" -ForegroundColor $color
    }
}

Write-Host ''
Write-Host '== SUMMARY ==' -ForegroundColor Cyan
Write-Host "  Total: $total   Passed: $passed   Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { 'Green' } else { 'Red' })

if ($failed -gt 0) {
    Write-Host ''
    Write-Host 'Fix the failures above before going live. See PRE-CLASS-CHECKLIST.md for context.' -ForegroundColor Yellow
    exit 1
}

Write-Host ''
Write-Host 'You are clear for takeoff. Still need to verify manually:' -ForegroundColor Yellow
Write-Host '  - Sample invoice fixtures for Segment 3' -ForegroundColor Yellow
Write-Host "  - O'Reilly platform tab open, screen-share at 1080p" -ForegroundColor Yellow
Write-Host '  - claude mcp list (Context7 + other servers reachable)' -ForegroundColor Yellow
Write-Host '  - Phone silenced, water within reach' -ForegroundColor Yellow
exit 0
