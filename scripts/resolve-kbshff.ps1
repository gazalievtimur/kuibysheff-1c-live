#Requires -Version 5.1
<#
.SYNOPSIS
  Resolve the kbshff binary: KBSHFF_BIN / --agent-bin, PATH, or build from KUIBYSHEFF_SRC.

.PARAMETER AgentBin
  Explicit path to kbshff(.exe).

.PARAMETER Build
  Force cargo build from KUIBYSHEFF_SRC / sibling Agent-Kuibysheff even if PATH has kbshff.

.OUTPUTS
  Absolute path to kbshff binary (stdout).
#>
param(
    [string]$AgentBin = "",
    [switch]$Build
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Find-KuibysheffSrc {
    if ($env:KUIBYSHEFF_SRC -and (Test-Path -LiteralPath $env:KUIBYSHEFF_SRC -PathType Container)) {
        return (Resolve-Path -LiteralPath $env:KUIBYSHEFF_SRC).Path
    }
    $here = Resolve-Path (Join-Path $PSScriptRoot "..")
    foreach ($name in @("Agent-Kuibysheff", "Agent Kuibyshev")) {
        $candidate = Join-Path (Split-Path -Parent $here) $name
        if (Test-Path -LiteralPath (Join-Path $candidate "Cargo.toml") -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $null
}

function Get-ReleaseKbshff {
    param([string]$SrcRoot)
    $exe = Join-Path $SrcRoot "target\release\kbshff.exe"
    $bin = Join-Path $SrcRoot "target\release\kbshff"
    if (Test-Path -LiteralPath $exe -PathType Leaf) { return (Resolve-Path $exe).Path }
    if (Test-Path -LiteralPath $bin -PathType Leaf) { return (Resolve-Path $bin).Path }
    return $null
}

if ($AgentBin) {
    $path = [System.IO.Path]::GetFullPath($AgentBin)
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "kbshff binary not found: $path"
    }
    Write-Output $path
    return
}

if ($env:KBSHFF_BIN) {
    $path = [System.IO.Path]::GetFullPath($env:KBSHFF_BIN)
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "KBSHFF_BIN not found: $path"
    }
    Write-Output $path
    return
}

if (-not $Build) {
    $cmd = Get-Command kbshff -ErrorAction SilentlyContinue
    if ($null -ne $cmd -and $cmd.Source) {
        Write-Output (Resolve-Path -LiteralPath $cmd.Source).Path
        return
    }
}

$src = Find-KuibysheffSrc
if (-not $src) {
    throw @"
kbshff not found.

Install a release binary and ensure it is on PATH, or set one of:
  KBSHFF_BIN=C:\path\to\kbshff.exe
  KUIBYSHEFF_SRC=C:\path\to\Agent-Kuibysheff   (then: cargo build --release --bin kbshff)

See https://github.com/gazalievtimur/Agent-Kuibysheff
"@
}

Write-Host "Building kbshff from $src ..."
Push-Location $src
try {
    & cargo build --release -p agent_Kuibysheff --bin kbshff
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}

$built = Get-ReleaseKbshff -SrcRoot $src
if (-not $built) {
    throw "cargo build succeeded but target/release/kbshff was not found under $src"
}
Write-Output $built
