#Requires -Version 5.1
<#
.SYNOPSIS
  Entry point for the 1c-live «Склад» LLM eval (OneScript).
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

$oscript = Get-Command oscript -ErrorAction SilentlyContinue
if ($null -eq $oscript) {
    throw "oscript not found in PATH (install OneScript 2.0)"
}

$flags = @("-encoding=utf-8", (Join-Path $WorkflowDir "run.os"), "--repo-root", $RepoRoot)
if ($Config) { $flags += @("--config", $Config) }
if ($AgentBin) { $flags += @("--agent-bin", $AgentBin) }
if ($All) { $flags += "--all" }
if ($DryRun) { $flags += "--dry-run" }
if ($RequirePlatform) { $flags += "--require-platform" }
if ($WithSearxng) { $flags += "--with-searxng" }
if ($SkipBuild) { $flags += "--skip-build" }
foreach ($id in $TaskId) { $flags += @("--task-id", $id) }

& $oscript.Source @flags
exit $LASTEXITCODE
