<#
.SYNOPSIS
    Deploys the infrastructure and applications required to run the solution.
.PARAMETER DeploymentName
	The name of the deployment.
.PARAMETER Location
    The location of the deployment.
.PARAMETER IsLocal
    Whether the deployment is for a local development environment or complete Azure deployment.
.PARAMETER SkipInfrastructure
    Whether to skip the infrastructure deployment. Requires InfrastructureOutputs.json to exist in the infra directory.
.EXAMPLE
    .\Setup-Environment.ps1 -DeploymentName 'my-deployment' -Location 'westeurope' -SkipInfrastructure $false
.NOTES
    Author: James Croft
    Date: 2024-04-20
#>

param
(
    [Parameter(Mandatory = $true)]
    [string]$DeploymentName,
    [Parameter(Mandatory = $true)]
    [string]$Location,
    [Parameter(Mandatory = $false)]
    [bool]$IsLocal,
    [Parameter(Mandatory = $false)]
    [bool]$SkipInfrastructure
)

Write-Host "Starting environment setup..."

if ($SkipInfrastructure -eq $false) {
    Write-Host "Deploying infrastructure..."
    $InfrastructureOutputs = (./infra/Deploy-Infrastructure.ps1 `
            -DeploymentName $DeploymentName `
            -Location $Location `
            -ErrorAction Stop)
}
else {
    Write-Host "Skipping infrastructure deployment. Using existing outputs..."
    $InfrastructureOutputs = Get-Content -Path './infra/InfrastructureOutputs.json' -Raw | ConvertFrom-Json
}

$OpenAIEndpoint = $InfrastructureOutputs.aiServicesInfo.value.openAIEndpoint
$OpenAICompletionDeployment = $InfrastructureOutputs.aiServicesInfo.value.modelDeploymentName
$StorageAccountName = $InfrastructureOutputs.storageAccountInfo.value.name

Write-Host "Updating local settings..."

$LocalSettingsPath = './src/AIDocumentPipeline/local.settings.json'
$LocalSettings = Get-Content -Path $LocalSettingsPath -Raw | ConvertFrom-Json
$LocalSettings.Values.OPENAI_ENDPOINT = $OpenAIEndpoint
$LocalSettings.Values.OPENAI_COMPLETION_DEPLOYMENT = $OpenAICompletionDeployment
$LocalSettings.Values.INVOICES_STORAGE_ACCOUNT_NAME = $StorageAccountName
$LocalSettings | ConvertTo-Json | Out-File -FilePath $LocalSettingsPath -Encoding utf8

if ($IsLocal -eq $true) {
    Write-Host "Starting local environment..."

    docker-compose up
}
else {
    Write-Host "Deploying AI Document Pipeline app..."

    ./infra/apps/AIDocumentPipeline/Deploy-App.ps1 `
        -InfrastructureOutputsPath './infra/InfrastructureOutputs.json' `
        -ErrorAction Stop
}
