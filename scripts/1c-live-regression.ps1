#Requires -Version 5.1
# Thin wrapper: oscript scripts/1c-live-regression.os
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs = @()
)
$oscript = Get-Command oscript -ErrorAction SilentlyContinue
if ($null -eq $oscript) {
    throw "oscript not found in PATH (install OneScript 2.0)"
}
$all = @("-encoding=utf-8", (Join-Path $PSScriptRoot "1c-live-regression.os"))
if ($RemainingArgs) { $all += $RemainingArgs }
& $oscript.Source @all
exit $LASTEXITCODE
