#Requires -Version 5.1
<#
.SYNOPSIS
  Entry point for the 1c-live «Склад» LLM eval.

.DESCRIPTION
  Resolves kbshff, runs eval.py (default gate task cfe-qty-check-01), then
  assert_regression.py.
#>
param(
    [string]$RepoRoot = "",
    [string]$Config = "",
    [string[]]$TaskId = @(),
    [switch]$All,
    [switch]$DryRun,
    [switch]$RequirePlatform,
    [switch]$WithSearxng,
    [switch]$SkipBuild,
    [string]$AgentBin = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WorkflowDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $WorkflowDir "..")).Path
}
else {
    $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
}

Set-Location $RepoRoot

if (-not $env:PYTHONIOENCODING) {
    $env:PYTHONIOENCODING = "utf-8"
}
if (-not $env:KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP) {
    $env:KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP = "1"
}

$dotenv = Join-Path $RepoRoot "scripts\import-dotenv.ps1"
if (Test-Path -LiteralPath $dotenv -PathType Leaf) {
    . $dotenv
    Import-DotEnv (Join-Path $RepoRoot ".env")
}

if ($DryRun) {
    python (Join-Path $WorkflowDir "eval.py") --dry-run `
        --bank-dir (Join-Path $WorkflowDir "bank") `
        --cf-dir (Join-Path $WorkflowDir "cf")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "1c-live dry-run OK."
    exit 0
}

if (-not $AgentBin) {
    $resolveArgs = @{}
    if (-not $SkipBuild) { $resolveArgs.Build = $true }
    $resolveExit = 0
    try {
        $AgentBin = & (Join-Path $RepoRoot "scripts\resolve-kbshff.ps1") @resolveArgs
        if (Test-Path variable:/LASTEXITCODE) { $resolveExit = [int]$LASTEXITCODE }
    } catch {
        throw "Failed to resolve kbshff: $($_.Exception.Message)"
    }
    if ($resolveExit -ne 0 -or [string]::IsNullOrWhiteSpace(($AgentBin | Out-String).Trim())) {
        throw "Failed to resolve kbshff"
    }
    $AgentBin = ($AgentBin | Select-Object -Last 1).ToString().Trim()
}

if (-not $Config) {
    $localConfig = Join-Path $RepoRoot "agent-config.local.yaml"
    $example = Join-Path $RepoRoot "profiles\1c-analyst\agent-config.example.yaml"
    if (Test-Path -LiteralPath $localConfig -PathType Leaf) {
        $Config = $localConfig
    }
    else {
        $Config = $example
    }
}

$pyArgs = @(
    (Join-Path $WorkflowDir "eval.py"),
    "--repo-root", $RepoRoot,
    "--config", $Config,
    "--bank-dir", (Join-Path $WorkflowDir "bank"),
    "--cf-dir", (Join-Path $WorkflowDir "cf"),
    "--runs-root", (Join-Path $WorkflowDir "runs"),
    "--agent-bin", $AgentBin
)

if ($All) {
    $pyArgs += "--all"
}
elseif ($TaskId.Count -gt 0) {
    foreach ($id in $TaskId) { $pyArgs += @("--task-id", $id) }
}
if ($RequirePlatform) { $pyArgs += "--require-platform" }
if ($WithSearxng) { $pyArgs += "--with-searxng" }

Write-Host "Using kbshff: $AgentBin"
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    python @pyArgs
    $evalExit = 0
    if (Test-Path variable:/LASTEXITCODE) { $evalExit = [int]$LASTEXITCODE }
} finally {
    $ErrorActionPreference = $prevEap
}
if ($evalExit -ne 0) { exit $evalExit }

$latest = Get-ChildItem -LiteralPath (Join-Path $WorkflowDir "runs") -Directory -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $latest) {
    throw "No runs/ directory after eval"
}
$report = Join-Path $latest.FullName "report.json"
python (Join-Path $WorkflowDir "assert_regression.py") $report
exit $LASTEXITCODE
