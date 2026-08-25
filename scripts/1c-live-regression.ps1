#Requires -Version 5.1
# Thin wrapper: harness/run.ps1
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs = @()
)
& (Join-Path $PSScriptRoot "..\harness\run.ps1") @RemainingArgs
exit $LASTEXITCODE
