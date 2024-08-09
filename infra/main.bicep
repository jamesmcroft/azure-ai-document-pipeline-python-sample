import { modelDeploymentInfo, raiPolicyInfo } from './ai_ml/ai-services.bicep'

targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the workload which is used to generate a short unique hash used in all resources.')
param workloadName string

@minLength(1)
@description('Primary location for all resources.')
param location string

@description('Name of the resource group. If empty, a unique name will be generated.')
param resourceGroupName string = ''

@description('Tags for all resources.')
param tags object = {
  WorkloadName: workloadName
  Environment: 'Dev'
}

@description('Principal ID of the user that will be granted permission to access services.')
param userPrincipalId string

@description('Responsible AI policies for the Azure AI Services instance.')
param raiPolicies raiPolicyInfo[] = [
  {
    name: workloadName
    mode: 'Blocking'
    prompt: {
      violence: { allowedContentLevel: 'High', blocking: true, enabled: true }
      hate: { allowedContentLevel: 'High', blocking: true, enabled: true }
      sexual: { allowedContentLevel: 'High', blocking: true, enabled: true }
      selfharm: { allowedContentLevel: 'High', blocking: true, enabled: true }
      jailbreak: { blocking: true, enabled: true }
      indirect_attack: { blocking: true, enabled: true }
    }
    completion: {
      violence: { allowedContentLevel: 'High', blocking: true, enabled: true }
      hate: { allowedContentLevel: 'High', blocking: true, enabled: true }
      sexual: { allowedContentLevel: 'High', blocking: true, enabled: true }
      selfharm: { allowedContentLevel: 'High', blocking: true, enabled: true }
      protected_material_text: { blocking: true, enabled: true }
      protected_material_code: { blocking: false, enabled: true }
    }
  }
]

@description('Model deployments for the Azure AI Services instance.')
param aiServiceModelDeployments modelDeploymentInfo[] = [
  {
    name: 'gpt-4o'
    model: { format: 'OpenAI', name: 'gpt-4o', version: '2024-05-13' }
    sku: { name: 'GlobalStandard', capacity: 30 }
    raiPolicyName: workloadName
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
]

var abbrs = loadJsonContent('./abbreviations.json')
var roles = loadJsonContent('./roles.json')
var resourceToken = toLower(uniqueString(subscription().id, workloadName, location))

resource contributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.general.contributor
}

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.managementGovernance.resourceGroup}${workloadName}'
  location: location
  tags: union(tags, {})
}

module managedIdentity './security/managed-identity.bicep' = {
  name: '${abbrs.security.managedIdentity}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.security.managedIdentity}${resourceToken}'
    location: location
    tags: union(tags, {})
  }
}

module resourceGroupRoleAssignment './security/resource-group-role-assignment.bicep' = {
  name: '${resourceGroup.name}-role-assignment'
  scope: resourceGroup
  params: {
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: contributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: contributor.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

// Required RBAC roles for Azure Functions to access the storage account
// https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob&pivots=programming-language-python#connecting-to-host-storage-with-an-identity
resource storageAccountContributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.storage.storageAccountContributor
}

resource storageBlobDataContributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.storage.storageBlobDataContributor
}

resource storageBlobDataOwner 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: resourceGroup
  name: roles.storage.storageBlobDataOwner
}

resource storageFileDataPrivilegedContributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.storage.storageFileDataPrivilegedContributor
}

resource storageTableDataContributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.storage.storageTableDataContributor
}

resource storageQueueDataContributor 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: resourceGroup
  name: roles.storage.storageQueueDataContributor
}

module storageAccount './storage/storage-account.bicep' = {
  name: '${abbrs.storage.storageAccount}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.storage.storageAccount}${resourceToken}'
    location: location
    tags: union(tags, {})
    sku: {
      name: 'Standard_LRS'
    }
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: storageAccountContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: storageAccountContributor.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: storageBlobDataContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: storageBlobDataContributor.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: storageBlobDataOwner.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: storageBlobDataOwner.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: storageFileDataPrivilegedContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: storageFileDataPrivilegedContributor.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: storageTableDataContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: storageTableDataContributor.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: storageQueueDataContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: storageQueueDataContributor.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

module invoicesContainer 'storage/storage-blob-container.bicep' = {
  name: '${abbrs.storage.storageAccount}${resourceToken}-invoices'
  scope: resourceGroup
  params: {
    name: 'invoices'
    storageAccountName: storageAccount.outputs.name
  }
}

resource keyVaultAdministrator 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: resourceGroup
  name: roles.security.keyVaultAdministrator
}

module keyVault './security/key-vault.bicep' = {
  name: '${abbrs.security.keyVault}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.security.keyVault}${resourceToken}'
    location: location
    tags: union(tags, {})
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: keyVaultAdministrator.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: keyVaultAdministrator.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

resource acrPush 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: resourceGroup
  name: roles.containers.acrPush
}

resource acrPull 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: resourceGroup
  name: roles.containers.acrPull
}

module containerRegistry 'containers/container-registry.bicep' = {
  name: '${abbrs.containers.containerRegistry}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.containers.containerRegistry}${resourceToken}'
    location: location
    tags: union(tags, {})
    sku: {
      name: 'Basic'
    }
    adminUserEnabled: true
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: acrPush.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: acrPush.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: acrPull.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: acrPull.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

module logAnalyticsWorkspace './management_governance/log-analytics-workspace.bicep' = {
  name: '${abbrs.managementGovernance.logAnalyticsWorkspace}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.managementGovernance.logAnalyticsWorkspace}${resourceToken}'
    location: location
    tags: union(tags, {})
  }
}

module applicationInsights './management_governance/application-insights.bicep' = {
  name: '${abbrs.managementGovernance.applicationInsights}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.managementGovernance.applicationInsights}${resourceToken}'
    location: location
    tags: union(tags, {})
    logAnalyticsWorkspaceName: logAnalyticsWorkspace.outputs.name
  }
}

module containerAppsEnvironment 'containers/container-apps-environment.bicep' = {
  name: '${abbrs.containers.containerAppsEnvironment}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.containers.containerAppsEnvironment}${resourceToken}'
    location: location
    tags: union(tags, {})
    logAnalyticsWorkspaceName: logAnalyticsWorkspace.outputs.name
  }
}

resource cognitiveServicesContributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.ai.cognitiveServicesContributor
}

resource cognitiveServicesOpenAIContributor 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.ai.cognitiveServicesOpenAIContributor
}

module aiServices './ai_ml/ai-services.bicep' = {
  name: '${abbrs.ai.aiServices}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.ai.aiServices}${resourceToken}'
    location: location
    tags: union(tags, {})
    identityId: managedIdentity.outputs.id
    raiPolicies: raiPolicies
    deployments: aiServiceModelDeployments
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: cognitiveServicesContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: cognitiveServicesContributor.id
        principalType: 'ServicePrincipal'
      }
      {
        principalId: userPrincipalId
        roleDefinitionId: cognitiveServicesOpenAIContributor.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: cognitiveServicesOpenAIContributor.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

resource azureMLDataScientist 'Microsoft.Authorization/roleDefinitions@2022-05-01-preview' existing = {
  scope: resourceGroup
  name: roles.ai.azureMLDataScientist
}

module aiHub './ai_ml/ai-hub.bicep' = {
  name: '${abbrs.ai.aiHub}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.ai.aiHub}${resourceToken}'
    friendlyName: 'Sample - AI Document Pipeline Hub'
    descriptionInfo: 'Generated by the AI Document Pipeline sample project'
    location: location
    tags: union(tags, {})
    identityId: managedIdentity.outputs.id
    storageAccountId: storageAccount.outputs.id
    keyVaultId: keyVault.outputs.id
    applicationInsightsId: applicationInsights.outputs.id
    containerRegistryId: containerRegistry.outputs.id
    aiServicesName: aiServices.outputs.name
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: azureMLDataScientist.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: azureMLDataScientist.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

module aiHubProject './ai_ml/ai-hub-project.bicep' = {
  name: '${abbrs.ai.aiHubProject}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.ai.aiHubProject}${resourceToken}'
    friendlyName: 'Sample - AI Document Pipeline Project'
    descriptionInfo: 'Generated by the AI Document Pipeline sample project'
    location: location
    tags: union(tags, {})
    identityId: managedIdentity.outputs.id
    aiHubName: aiHub.outputs.name
    roleAssignments: [
      {
        principalId: userPrincipalId
        roleDefinitionId: azureMLDataScientist.id
        principalType: 'User'
      }
      {
        principalId: managedIdentity.outputs.principalId
        roleDefinitionId: azureMLDataScientist.id
        principalType: 'ServicePrincipal'
      }
    ]
  }
}

output subscriptionInfo object = {
  id: subscription().subscriptionId
  tenantId: subscription().tenantId
}

output resourceGroupInfo object = {
  id: resourceGroup.id
  name: resourceGroup.name
  location: resourceGroup.location
  workloadName: workloadName
}

output managedIdentityInfo object = {
  id: managedIdentity.outputs.id
  name: managedIdentity.outputs.name
  principalId: managedIdentity.outputs.principalId
  clientId: managedIdentity.outputs.clientId
}

output keyVaultInfo object = {
  id: keyVault.outputs.id
  name: keyVault.outputs.name
  uri: keyVault.outputs.uri
}

output containerRegistryInfo object = {
  id: containerRegistry.outputs.id
  name: containerRegistry.outputs.name
  loginServer: containerRegistry.outputs.loginServer
}

output logAnalyticsWorkspaceInfo object = {
  id: logAnalyticsWorkspace.outputs.id
  name: logAnalyticsWorkspace.outputs.name
  customerId: logAnalyticsWorkspace.outputs.customerId
}

output applicationInsightsInfo object = {
  id: applicationInsights.outputs.id
  name: applicationInsights.outputs.name
}

output storageAccountInfo object = {
  id: storageAccount.outputs.id
  name: storageAccount.outputs.name
  invoicesContainerName: invoicesContainer.outputs.name
}

output containerAppsEnvironmentInfo object = {
  id: containerAppsEnvironment.outputs.id
  name: containerAppsEnvironment.outputs.name
  defaultDomain: containerAppsEnvironment.outputs.defaultDomain
  staticIp: containerAppsEnvironment.outputs.staticIp
}

output aiServicesInfo object = {
  id: aiServices.outputs.id
  name: aiServices.outputs.name
  endpoint: aiServices.outputs.endpoint
  host: aiServices.outputs.host
  openAIEndpoint: aiServices.outputs.openAIEndpoint
  openAIHost: aiServices.outputs.openAIHost
  modelDeploymentName: aiServiceModelDeployments[0].name
}

output aiHubInfo object = {
  id: aiHub.outputs.id
  name: aiHub.outputs.name
  aiServicesConnectionName: aiHub.outputs.aiServicesConnectionName
  openAIServicesConnectionName: aiHub.outputs.openAIServicesConnectionName
}

output aiHubProjectInfo object = {
  id: aiHubProject.outputs.id
  name: aiHubProject.outputs.name
}
