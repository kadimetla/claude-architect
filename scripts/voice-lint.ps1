<#
.SYNOPSIS
    Lint all Markdown files AND notebook markdown cells against Tim Warner's voice rules.

.DESCRIPTION
    Verifies that no MD file under the repo root, and no markdown cell inside any
    .ipynb file under notebooks/, contains:
      - Em dashes (U+2014). Use ` - ` (hyphen with spaces), commas, or periods.
      - "AWS" mentions. Azure-first per Tim's stack defaults.
      - Glazing openers ("Great question", "You're absolutely right", "Excellent ...").

    The literal linter pattern in CLAUDE.md is whitelisted so this script does not
    flag the file that documents the rule. Notebook code cells are NOT scanned -
    only markdown cells, since the rules apply to prose. Exits non-zero on any
    violation so this is safe to wire into a pre-commit hook or GitHub Action.

.PARAMETER Path
    Repo root to scan. Defaults to the script's parent directory.

.EXAMPLE
    pwsh ./scripts/voice-lint.ps1
    Runs the linter against the whole repo.

.EXAMPLE
    npm run lint:voice
    Same thing via npm script.

.NOTES
    Author: Tim Warner
    The 2026-05-16 build leaked 18 em dashes into domain-2-tools-mcp.md
    despite explicit voice rules. This script exists so that never happens again.
#>

[CmdletBinding()]
param(
    [string]$Path = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

# Skip CLAUDE.md (scanned with tighter rules below) and PRACTICE-QUESTIONS.md
# (community-sourced from Paul Larionov's study repo; its disclaimer header
# covers voice drift per CLAUDE.md "Common operations" notes).
$mdFiles = Get-ChildItem -Path $Path -Filter '*.md' -File |
    Where-Object { $_.Name -notin @('CLAUDE.md', 'PRACTICE-QUESTIONS.md') }

# CLAUDE.md is allowed to contain em dashes inside the documented `grep -P "—|..."` linter pattern.
# Scan it with a tighter rule that excludes those specific lines.
$claudeMd = Join-Path $Path 'CLAUDE.md'

$violations = @()

foreach ($file in $mdFiles) {
    $lines = Get-Content -LiteralPath $file.FullName
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNo = $i + 1

        if ($line -match '—') {
            $violations += [pscustomobject]@{
                File = $file.Name; Line = $lineNo; Rule = 'em-dash'; Text = $line.Trim()
            }
        }
        # Allow AWS when the line is documenting the rule itself ("no AWS mentions",
        # "AWS mentions", or inside a grep example pattern). Catches real violations,
        # ignores meta-references in CLAUDE.md / INSTRUCTOR-SETUP.md / lint scripts.
        if ($line -match '\bAWS\b' -and $line -notmatch '(?i)(no AWS|AWS mentions|grep.*AWS|"AWS")') {
            $violations += [pscustomobject]@{
                File = $file.Name; Line = $lineNo; Rule = 'AWS'; Text = $line.Trim()
            }
        }
        if ($line -match '(?i)(great question|excellent question|you''re absolutely right|absolutely correct|that''s a great)') {
            $violations += [pscustomobject]@{
                File = $file.Name; Line = $lineNo; Rule = 'glazing'; Text = $line.Trim()
            }
        }
    }
}

# CLAUDE.md scan: only flag em dashes OUTSIDE the documented `grep -P "—..."` examples.
if (Test-Path $claudeMd) {
    $lines = Get-Content -LiteralPath $claudeMd
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNo = $i + 1
        # Allow em dashes inside CLAUDE.md when they appear in documented lint
        # patterns: grep examples, Python re.finditer / re.search calls, or
        # inside backtick-quoted strings (which call out the literal character).
        if ($line -match '—' -and $line -notmatch '(grep.*—|re\.finditer.*—|re\.search.*—|`.*—.*`)') {
            $violations += [pscustomobject]@{
                File = 'CLAUDE.md'; Line = $lineNo; Rule = 'em-dash'; Text = $line.Trim()
            }
        }
        # Allow AWS in CLAUDE.md ONLY when it appears inside the documented rule
        # ("No AWS mentions" / "AWS|" inside the grep example).
        if ($line -match '\bAWS\b' -and $line -notmatch '(No AWS mentions|grep.*AWS)') {
            $violations += [pscustomobject]@{
                File = 'CLAUDE.md'; Line = $lineNo; Rule = 'AWS'; Text = $line.Trim()
            }
        }
    }
}

# Notebook markdown cell scan. .ipynb files are JSON; we parse them, extract
# markdown cells, and apply the same rules (em-dash, AWS, glazing). Code cells
# are skipped - the rules apply to prose, and Python `~` glob patterns or
# regex literals inside code shouldn't be flagged as violations.
$nbDir = Join-Path $Path 'notebooks'
$nbFiles = @()
if (Test-Path $nbDir) {
    $nbFiles = Get-ChildItem -Path $nbDir -Filter '*.ipynb' -File
}

foreach ($nb in $nbFiles) {
    try {
        $json = Get-Content -LiteralPath $nb.FullName -Raw | ConvertFrom-Json
    } catch {
        $violations += [pscustomobject]@{
            File = $nb.Name; Line = 0; Rule = 'invalid-json'; Text = $_.Exception.Message
        }
        continue
    }

    for ($ci = 0; $ci -lt $json.cells.Count; $ci++) {
        $cell = $json.cells[$ci]
        if ($cell.cell_type -ne 'markdown') { continue }

        # cell.source can be a string or an array of strings
        $sourceLines = if ($cell.source -is [array]) { $cell.source } else { @($cell.source) }
        $joined = ($sourceLines -join '')
        $lineNo = 0
        foreach ($srcLine in ($joined -split "`n")) {
            $lineNo++
            if ($srcLine -match '—') {
                $violations += [pscustomobject]@{
                    File = "$($nb.Name)[cell $ci]"; Line = $lineNo; Rule = 'em-dash'; Text = $srcLine.Trim()
                }
            }
            if ($srcLine -match '\bAWS\b' -and $srcLine -notmatch '(?i)(no AWS|AWS mentions|grep.*AWS|"AWS")') {
                $violations += [pscustomobject]@{
                    File = "$($nb.Name)[cell $ci]"; Line = $lineNo; Rule = 'AWS'; Text = $srcLine.Trim()
                }
            }
            if ($srcLine -match '(?i)(great question|excellent question|you''re absolutely right|absolutely correct|that''s a great)') {
                $violations += [pscustomobject]@{
                    File = "$($nb.Name)[cell $ci]"; Line = $lineNo; Rule = 'glazing'; Text = $srcLine.Trim()
                }
            }
        }
    }
}

$totalScanned = $mdFiles.Count + 1 + $nbFiles.Count
if ($violations.Count -eq 0) {
    Write-Host 'voice-lint: OK (no violations across ' -NoNewline
    Write-Host "$($mdFiles.Count + 1) MD + $($nbFiles.Count) ipynb files)" -ForegroundColor Green
    exit 0
}

Write-Host "voice-lint: $($violations.Count) violation(s) found across $totalScanned files" -ForegroundColor Red
$violations | Format-Table File, Line, Rule, Text -AutoSize -Wrap
exit 1
