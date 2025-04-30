pipeline {
    agent any
    environment {
        // Customizable Variables
        ACR_NAME          = 'mywebacr'           // Your Azure Container Registry name
        DOCKER_IMAGE      = 'myweb-app'          // Your Docker image name
        AKS_NAMESPACE     = 'myweb-ns'           // Kubernetes namespace
        RESOURCE_GROUP    = 'myweb-rg'           // Azure resource group
        AKS_CLUSTER       = 'myweb-aks'          // AKS cluster name
        GIT_REPO          = 'https://github.com/mulukelem/solapp-cicd-poc.git'  // Your repo URL
    }

    stages {
        // Stage 1: Secure Code Checkout with GitHub PAT
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
                        url: "${GIT_REPO}",
                        credentialsId: 'github-pat'  // Jenkins credential for GitHub PAT
                    ]]
                ])
                sh 'echo "✅ Code checkout completed"'
            }
        }

        // Stage 2: Docker Build & Push to ACR
        stage('Build and Push to ACR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'acr-credentials',
                    usernameVariable: 'ACR_USER',
                    passwordVariable: 'ACR_PASS'
                )]) {
                    sh """
                        docker build -t ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest ./src
                        echo ${ACR_PASS} | docker login ${ACR_NAME}.azurecr.io -u ${ACR_USER} --password-stdin
                        docker push ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest
                    """
                }
                sh 'echo "✅ Image built and pushed to ACR"'
            }
        }

        // Stage 3: Deploy to AKS with Namespace Automation
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
                        # Azure Authentication
                        az login --service-principal \
                            -u \$AZURE_CLIENT_ID \
                            -p \$AZURE_CLIENT_SECRET \
                            --tenant \$AZURE_TENANT_ID

                        # Get AKS credentials
                        az aks get-credentials \
                            --resource-group ${RESOURCE_GROUP} \
                            --name ${AKS_CLUSTER} \
                            --overwrite-existing

                        # Create namespace if not exists (idempotent)
                        kubectl create namespace ${AKS_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

                        # Deploy application
                        kubectl apply -f k8s/deployment.yaml -n ${AKS_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${AKS_NAMESPACE}

                        # Verify deployment
                        kubectl rollout status deployment/myweb-deployment -n ${AKS_NAMESPACE} --timeout=90s
                        
                        # Print application URL
                        echo "Application deployed successfully!"
                        echo "Access URL: http://\$(kubectl get svc myweb-service -n ${AKS_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
                    """
                }
            }
        }
    }

    post {
        always {
            // Cleanup Docker credentials
            sh 'docker logout ${ACR_NAME}.azurecr.io || true'
            cleanWs()
            
            // Print final status
            script {
                echo "Pipeline ${currentBuild.result ?: 'SUCCESS'}"
            }
        }
    }
}
