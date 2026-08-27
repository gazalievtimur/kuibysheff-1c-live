#Requires -Version 5.1
param(
    [string]$AgentBin = "",
    [switch]$Build
)
$oscript = Get-Command oscript -ErrorAction SilentlyContinue
if ($null -eq $oscript) {
    throw "oscript not found in PATH (install OneScript 2.0)"
}
$flags = @("-encoding=utf-8", (Join-Path $PSScriptRoot "resolve-kbshff.os"))
if ($AgentBin) { $flags += @("--agent-bin", $AgentBin) }
if ($Build) { $flags += "--build" }
& $oscript.Source @flags
exit $LASTEXITCODE
