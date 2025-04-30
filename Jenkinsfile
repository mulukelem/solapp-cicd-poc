pipeline {
    agent any
    environment {
        ACR_NAME = "mywebacr"                  // Your ACR name
        DOCKER_IMAGE = "myweb-app"              // Your image name
        AKS_NAMESPACE = "myweb-ns"              // K8s namespace
    }

    stages {
        // STAGE 1: Checkout with GitHub PAT
        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: 'main']],
                    extensions: [
                        [$class: 'CleanBeforeCheckout'],
                        [$class: 'CloneOption', depth: 1, shallow: true]
                    ],
                    userRemoteConfigs: [[
                        url: 'https://github.com/mulukelem/myweb-cicd.git',  // Your repo
                        credentialsId: 'github-pat'  // 🚨 MATCHES JENKINS CREDENTIAL ID
                    ]]
                ])
            }
        }

        // STAGE 2: Build & Push to ACR
        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'acr-credentials',
                    usernameVariable: 'ACR_USER',
                    passwordVariable: 'ACR_PASS'
                )]) {
                    sh """
                        docker build -t ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest ./src
                        docker login ${ACR_NAME}.azurecr.io -u $ACR_USER -p $ACR_PASS
                        docker push ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        // STAGE 3: Deploy to AKS
        stage('Deploy to AKS') {
            steps {
                withCredentials([azureServicePrincipal(
                    credentialsId: 'azure-credentials',
                    subscriptionIdVariable: 'AZURE_SUBSCRIPTION_ID',
                    clientIdVariable: 'AZURE_CLIENT_ID',
                    clientSecretVariable: 'AZURE_CLIENT_SECRET',
                    tenantIdVariable: 'AZURE_TENANT_ID'
                )]) {
                    sh """
                        az login --service-principal \
                            -u \$AZURE_CLIENT_ID \
                            -p \$AZURE_CLIENT_SECRET \
                            --tenant \$AZURE_TENANT_ID
                        az aks get-credentials \
                            --resource-group myweb-rg \
                            --name myweb-aks \
                            --overwrite-existing
                        kubectl apply -f k8s/deployment.yaml -n ${AKS_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${AKS_NAMESPACE}
                    """
                }
            }
        }
    }
}
