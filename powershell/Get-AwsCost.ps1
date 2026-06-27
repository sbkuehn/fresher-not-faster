<#
.SYNOPSIS
    Month-to-date AWS cost by service via AWS Tools for PowerShell.

.DESCRIPTION
    Companion code for the article "Fresher Is Not Faster". The same
    lagged read as the AWS CLI example, returned as objects you can pipe.

.PARAMETER Start
    Start date (inclusive). Defaults to the first of the current month.

.PARAMETER End
    End date (exclusive). Defaults to today.

.EXAMPLE
    .\Get-AwsCost.ps1

.EXAMPLE
    .\Get-AwsCost.ps1 -Start 2026-06-01 -End 2026-06-17

.NOTES
    Project : Fresher Is Not Faster (companion code)
    Author  : Shannon Eldridge-Kuehn
    Created : 2026-06-26
    Version : 1.0.0
    License : MIT
    Requires: AWS.Tools.CostExplorer, configured credentials.
    Note    : each Cost Explorer call costs about USD 0.01.
#>

[CmdletBinding()]
param(
    [string]$Start = (Get-Date -Format 'yyyy-MM-01'),
    [string]$End   = (Get-Date -Format 'yyyy-MM-dd')
)

Get-CECostAndUsage `
    -TimePeriod_Start $Start `
    -TimePeriod_End $End `
    -Granularity DAILY `
    -Metric UnblendedCost `
    -GroupBy @{ Type = 'DIMENSION'; Key = 'SERVICE' } `
    -Region us-east-1
