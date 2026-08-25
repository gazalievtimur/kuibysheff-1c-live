#Requires -Version 5.1
<#
.SYNOPSIS
  Optional YAxUnit / platform step for 1c-live.

.DESCRIPTION
  Without 1C platform tools (ibcmd / 1cv8) the script prints SKIP and exits 0
  unless -RequirePlatform is set (then exit 1).

  When platform tools are present this is a stub orchestration hook:
  create work dir, copy CF + YAxUnit CFE (prefer generated implementer/yaxunit
  out/cfe-tests; fixture cfe/YAxUnit_Tests_Sklad is the eval fallback) + agent
  feature CFE, and leave a checklist for ibcmd load / unit run. Full Designer
  automation varies by install layout.
#>
param(
    [Parameter(Mandatory = $true)][string]$CfDir,
    [Parameter(Mandatory = $true)][string]$YaxUnitDir,
    [Parameter(Mandatory = $true)][string]$AgentCfeDir,
    [Parameter(Mandatory = $true)][string]$WorkDir,
    [switch]$RequirePlatform
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Find-Ibcmd {
    $fromEnv = $env:IBCMD_PATH
    if ($fromEnv -and (Test-Path -LiteralPath $fromEnv -PathType Leaf)) {
        return (Resolve-Path -LiteralPath $fromEnv).Path
    }
    $candidates = @(
        "C:\Program Files\1cv8\*\bin\ibcmd.exe",
        "C:\Program Files (x86)\1cv8\*\bin\ibcmd.exe"
    )
    foreach ($pattern in $candidates) {
        $hit = Get-Item -Path $pattern -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($hit) {
            return $hit.FullName
        }
    }
    return $null
}

New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
$checklist = Join-Path $WorkDir "platform-checklist.md"

$ibcmd = Find-Ibcmd
if (-not $ibcmd) {
    $msg = "SKIP: ibcmd not found (set IBCMD_PATH or install 1C platform)."
    Write-Host $msg
    @"
# Platform step skipped

$msg

Prepared paths (for manual run):
- CF: $CfDir
- YAxUnit CFE: $YaxUnitDir
- Agent CFE: $AgentCfeDir
"@ | Set-Content -LiteralPath $checklist -Encoding UTF8
    if ($RequirePlatform) {
        Write-Error $msg
        exit 1
    }
    exit 0
}

if (-not (Test-Path -LiteralPath $AgentCfeDir -PathType Container)) {
    $msg = "Agent CFE directory missing: $AgentCfeDir"
    if ($RequirePlatform) {
        Write-Error $msg
        exit 1
    }
    Write-Host "SKIP: $msg"
    exit 0
}

$ibDir = Join-Path $WorkDir "ib"
$cfgCopy = Join-Path $WorkDir "cf"
$extYax = Join-Path $WorkDir "cfe-yaxunit"
$extAgent = Join-Path $WorkDir "cfe-agent"

if (Test-Path -LiteralPath $cfgCopy) { Remove-Item -Recurse -Force -LiteralPath $cfgCopy }
if (Test-Path -LiteralPath $extYax) { Remove-Item -Recurse -Force -LiteralPath $extYax }
if (Test-Path -LiteralPath $extAgent) { Remove-Item -Recurse -Force -LiteralPath $extAgent }
Copy-Item -Recurse -Force -LiteralPath $CfDir -Destination $cfgCopy
Copy-Item -Recurse -Force -LiteralPath $YaxUnitDir -Destination $extYax
Copy-Item -Recurse -Force -LiteralPath $AgentCfeDir -Destination $extAgent

@"
# 1c-live platform checklist

ibcmd: $ibcmd
work: $WorkDir

Suggested flow (adjust to your platform version):

1. Create file IB under ``$ibDir``
2. Load configuration from ``$cfgCopy``
3. Load extension ``$extYax``
4. Load extension ``$extAgent``
5. Run YAxUnit suites referenced by the task expect.yaxunit

This harness verifies that inputs exist and platform tooling is discoverable.
Full automated unit execution is install-specific; treat a successful discovery
plus prepared trees as the optional platform gate for now.
"@ | Set-Content -LiteralPath $checklist -Encoding UTF8

Write-Host "OK: platform tools found ($ibcmd); trees prepared under $WorkDir"
Write-Host "See $checklist"
exit 0
