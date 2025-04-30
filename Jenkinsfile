pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'myweb-app'
        ACR_NAME = 'mywebacr'
        AKS_NAMESPACE = 'myweb-ns'
        DEPLOYMENT_NAME = 'myweb-deployment'
        SERVICE_NAME = 'myweb-service'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/mulukelem/solapp-cicd-poc.git', branch: 'main'
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'acr-credentials',
                        usernameVariable: 'ACR_USER',
                        passwordVariable: 'ACR_PASS'
                    )]) {
                        sh "docker build -t ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest ./src"
                        sh "docker login ${ACR_NAME}.azurecr.io -u ${ACR_USER} -p ${ACR_PASS}"
                        sh "docker push ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([azureServicePrincipal(
                    credentialsId: 'azure-credentials',
                    subscriptionIdVariable: 'AZURE_SUBSCRIPTION_ID',
                    clientIdVariable: 'AZURE_CLIENT_ID',
                    clientSecretVariable: 'AZURE_CLIENT_SECRET',
                    tenantIdVariable: 'AZURE_TENANT_ID'
                )]) {
                    sh """
                        az login --service-principal -u \$AZURE_CLIENT_ID -p \$AZURE_CLIENT_SECRET --tenant \$AZURE_TENANT_ID
                        az aks get-credentials --resource-group myweb-rg --name myweb-aks --overwrite-existing
                        kubectl apply -f k8s/deployment.yaml -n ${AKS_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${AKS_NAMESPACE}
                    """
                }
            }
        }
    }
}
