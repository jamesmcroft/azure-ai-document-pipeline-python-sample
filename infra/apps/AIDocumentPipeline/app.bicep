targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the workload which is used to generate a short unique hash used in all resources.')
param workloadName string

@minLength(1)
@description('Primary location for all resources.')
param location string

@description('Tags for all resources.')
param tags object = {}

@description('Name of the container image.')
param containerImageName string

@description('Primary location for the deployed Document Intelligence service. Default is westeurope for latest preview support.')
param documentIntelligenceLocation string = 'westeurope'

@description('Location of the Azure OpenAI service for the application. Default is swedencentral.')
param openAILocation string = 'swedencentral'
@description('Name of the Azure OpenAI completion model for the application. Default is gpt-35-turbo.')
param openAICompletionModelName string = 'gpt-35-turbo'
@description('Name of the Azure OpenAI vision completion model for the application. Default is gpt-4.')
param openAIVisionCompletionModelName string = 'gpt-4'
@description('Name of the Azure OpenAI embedding model for the application. Default is text-embedding-ada-002.')
param openAIEmbeddingModelName string = 'text-embedding-ada-002'

var abbrs = loadJsonContent('../../abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, workloadName, location))
var documentIntelligenceResourceToken = toLower(uniqueString(
  subscription().id,
  workloadName,
  documentIntelligenceLocation
))
var openAIResourceToken = toLower(uniqueString(subscription().id, workloadName, openAILocation))

resource managedIdentityRef 'Microsoft.ManagedIdentity/userAssignedIdentities@2022-01-31-preview' existing = {
  name: '${abbrs.security.managedIdentity}${resourceToken}'
}

resource containerRegistryRef 'Microsoft.ContainerRegistry/registries@2022-12-01' existing = {
  name: '${abbrs.containers.containerRegistry}${resourceToken}'
}

resource applicationInsightsRef 'Microsoft.Insights/components@2020-02-02' existing = {
  name: '${abbrs.managementGovernance.applicationInsights}${resourceToken}'
}

resource storageAccountRef 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: '${abbrs.storage.storageAccount}${resourceToken}'
}

resource documentIntelligenceRef 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' existing = {
  name: '${abbrs.ai.documentIntelligence}${documentIntelligenceResourceToken}'
}

resource openAIRef 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' existing = {
  name: '${abbrs.ai.openAIService}${openAIResourceToken}'
}

resource containerAppsEnvironmentRef 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: '${abbrs.containers.containerAppsEnvironment}${resourceToken}'
}

var appToken = toLower(uniqueString(subscription().id, workloadName, location, 'ai-document-pipeline'))
var functionsWebJobStorageVariableName = 'AzureWebJobsStorage'
var invoicesConnectionStringVariableName = 'INVOICES_QUEUE_CONNECTION'
var applicationInsightsConnectionStringSecretName = 'applicationinsightsconnectionstring'

module invoicesQueue '../../storage/storage-queue.bicep' = {
  name: '${abbrs.storage.storageAccount}${appToken}'
  params: {
    name: 'invoices'
    storageAccountName: storageAccountRef.name
  }
}

module containerApp '../../containers/container-app.bicep' = {
  name: '${abbrs.containers.containerApp}${appToken}'
  params: {
    name: '${abbrs.containers.containerApp}${appToken}'
    location: location
    tags: union(tags, { App: 'ai-document-pipeline' })
    containerAppsEnvironmentId: containerAppsEnvironmentRef.id
    containerAppIdentityId: managedIdentityRef.id
    imageInContainerRegistry: true
    containerRegistryName: containerRegistryRef.name
    containerImageName: containerImageName
    containerIngress: {
      external: true
      targetPort: 80
      transport: 'auto'
      allowInsecure: false
    }
    containerScale: {
      minReplicas: 1
      maxReplicas: 3
      rules: [
        {
          name: 'http'
          http: {
            metadata: {
              concurrentRequests: '20'
            }
          }
        }
      ]
    }
    secrets: [
      {
        name: applicationInsightsConnectionStringSecretName
        value: applicationInsightsRef.properties.ConnectionString
      }
    ]
    environmentVariables: [
      {
        name: 'AzureWebJobsFeatureFlags'
        value: 'EnableWorkerIndexing'
      }
      {
        name: 'FUNCTIONS_EXTENSION_VERSION'
        value: '~4'
      }
      {
        name: 'FUNCTIONS_WORKER_RUNTIME'
        value: 'python'
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        secretRef: applicationInsightsConnectionStringSecretName
      }
      {
        name: '${functionsWebJobStorageVariableName}__accountName'
        value: storageAccountRef.name
      }
      {
        name: '${functionsWebJobStorageVariableName}__credential'
        value: 'managedidentity'
      }
      {
        name: '${functionsWebJobStorageVariableName}__clientId'
        value: managedIdentityRef.properties.clientId
      }
      {
        name: 'MANAGED_IDENTITY_CLIENT_ID'
        value: managedIdentityRef.properties.clientId
      }
      {
        name: 'DOCUMENT_INTELLIGENCE_ENDPOINT'
        value: documentIntelligenceRef.properties.endpoint
      }
      {
        name: 'OPENAI_ENDPOINT'
        value: openAIRef.properties.endpoint
      }
      {
        name: 'OPENAI_COMPLETION_MODEL_DEPLOYMENT'
        value: openAICompletionModelName
      }
      {
        name: 'OPENAI_VISION_COMPLETION_MODEL_DEPLOYMENT'
        value: openAIVisionCompletionModelName
      }
      {
        name: 'OPENAI_EMBEDDING_MODEL_DEPLOYMENT'
        value: openAIEmbeddingModelName
      }
      {
        name: 'INVOICES_STORAGE_ACCOUNT_NAME'
        value: storageAccountRef.name
      }
      {
        name: '${invoicesConnectionStringVariableName}__accountName'
        value: storageAccountRef.name
      }
      {
        name: '${invoicesConnectionStringVariableName}__credential'
        value: 'managedidentity'
      }
      {
        name: '${invoicesConnectionStringVariableName}__clientId'
        value: managedIdentityRef.properties.clientId
      }
      {
        name: 'WEBSITE_HOSTNAME'
        value: 'localhost'
      }
    ]
  }
}

output containerAppInfo object = {
  id: containerApp.outputs.id
  name: containerApp.outputs.name
  fqdn: containerApp.outputs.fqdn
  url: containerApp.outputs.url
  latestRevisionFqdn: containerApp.outputs.latestRevisionFqdn
  latestRevisionUrl: containerApp.outputs.latestRevisionUrl
}
