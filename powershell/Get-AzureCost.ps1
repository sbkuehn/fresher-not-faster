<#
.SYNOPSIS
    Month-to-date Azure cost by service via the Cost Management Query API.

.DESCRIPTION
    Companion code for the article "Fresher Is Not Faster". Returns the
    same lagged read as the portal, as PowerShell objects you can pipe,
    format, or push into Log Analytics.

.PARAMETER SubscriptionId
    The Azure subscription to query. Defaults to the AZURE_SUBSCRIPTION_ID
    environment variable.

.EXAMPLE
    Connect-AzAccount
    .\Get-AzureCost.ps1 -SubscriptionId 00000000-0000-0000-0000-000000000000

.EXAMPLE
    $env:AZURE_SUBSCRIPTION_ID = '00000000-0000-0000-0000-000000000000'
    .\Get-AzureCost.ps1

.NOTES
    Project : Fresher Is Not Faster (companion code)
    Author  : Shannon Eldridge-Kuehn
    Created : 2026-06-26
    Version : 1.0.0
    License : MIT
    Requires: Az.Accounts, Az.CostManagement
#>

[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID
)

if (-not $SubscriptionId) {
    throw "Provide -SubscriptionId or set AZURE_SUBSCRIPTION_ID."
}

Invoke-AzCostManagementQuery `
    -Type ActualCost `
    -Timeframe MonthToDate `
    -Scope "/subscriptions/$SubscriptionId" `
    -DatasetGranularity Daily `
    -DatasetAggregation @{ totalCost = @{ name = 'Cost'; function = 'Sum' } } `
    -DatasetGrouping @(@{ type = 'Dimension'; name = 'ServiceName' })
