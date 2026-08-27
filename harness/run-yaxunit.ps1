#Requires -Version 5.1
param(
    [Parameter(Mandatory = $true)][string]$CfDir,
    [Parameter(Mandatory = $true)][string]$YaxUnitDir,
    [Parameter(Mandatory = $true)][string]$AgentCfeDir,
    [Parameter(Mandatory = $true)][string]$WorkDir,
    [switch]$RequirePlatform
)
$oscript = Get-Command oscript -ErrorAction SilentlyContinue
if ($null -eq $oscript) {
    throw "oscript not found in PATH (install OneScript 2.0)"
}
$flags = @(
    "-encoding=utf-8",
    (Join-Path $PSScriptRoot "run-yaxunit.os"),
    "--cf-dir", $CfDir,
    "--yaxunit-dir", $YaxUnitDir,
    "--agent-cfe-dir", $AgentCfeDir,
    "--work-dir", $WorkDir
)
if ($RequirePlatform) { $flags += "--require-platform" }
& $oscript.Source @flags
exit $LASTEXITCODE
