pipeline {
    agent any

    environment {
        APP_NAME = 'argo-deepdive-api'
        GIT_SHORT_SHA = "${sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}"
    }

    stages {
        stage('Determine Image Version') {
            steps {
                script {
                    if (env.TAG_NAME) {
                        env.IMAGE_TAG = "${env.TAG_NAME}"
                        env.TARGET_GITOPS_BRANCH = "main"
                    } else {
                        env.IMAGE_TAG = "${env.BRANCH_NAME}-${env.GIT_SHORT_SHA}"
                        env.TARGET_GITOPS_BRANCH = "${env.BRANCH_NAME}"
                    }
                    echo "Determined Image Tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build & Push Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        env.IMAGE = "${DOCKER_USER}/${env.APP_NAME}:${env.IMAGE_TAG}"
                    }
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        
                        echo "Building Docker image: ${env.IMAGE}"
                        docker build --build-arg APP_VERSION=${env.IMAGE_TAG} -t ${env.IMAGE} .
                        
                        echo "Pushing to Docker Hub..."
                        docker push ${env.IMAGE}
                    """
                }
            }
        }
        
        // Note: The 'Update GitOps Manifests' stage will be added later 
        // after we create the deepdive-gitops repository!
    }
}
