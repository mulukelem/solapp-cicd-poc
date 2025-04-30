pipeline {
    agent any
    environment {
        // Customizable Variables
        ACR_NAME          = 'mywebacr'           // Your ACR name
        DOCKER_IMAGE      = 'myweb-app'          // Image name
        AKS_NAMESPACE     = 'myweb-ns'           // K8s namespace
        RESOURCE_GROUP    = 'myweb-rg'           // Azure RG
        AKS_CLUSTER       = 'myweb-aks'          // AKS cluster
    }

    stages {
        // Stage 1: Secure ACR Login & Build
        stage('Build and Push') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'acr-credentials', // Store ACR creds in Jenkins
                        usernameVariable: 'ACR_USER',
                        passwordVariable: 'ACR_PASS'
                    )]) {
                        sh """
                            # Auto-login to ACR
                            echo \$ACR_PASS | docker login ${ACR_NAME}.azurecr.io -u \$ACR_USER --password-stdin
                            
                            # Build and push
                            docker build -t ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest ./src
                            docker push ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }

        // Stage 2: Deploy to AKS
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
                        # Azure Login
                        az login --service-principal \
                            -u \$AZURE_CLIENT_ID \
                            -p \$AZURE_CLIENT_SECRET \
                            --tenant \$AZURE_TENANT_ID

                        # Attach ACR to AKS (idempotent)
                        az aks update -g ${RESOURCE_GROUP} -n ${AKS_CLUSTER} --attach-acr ${ACR_NAME}

                        # Deploy
                        kubectl apply -f k8s/deployment.yaml -n ${AKS_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${AKS_NAMESPACE}
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout ${ACR_NAME}.azurecr.io || true'  // Cleanup
        }
    }
}
