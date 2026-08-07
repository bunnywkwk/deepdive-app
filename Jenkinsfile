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
                        env.TARGET_GITOPS_FOLDER = "environments/production"
                    } else {
                        env.IMAGE_TAG = "${env.BRANCH_NAME}-${env.GIT_SHORT_SHA}"
                        env.TARGET_GITOPS_FOLDER = "environments/${env.BRANCH_NAME}"
                    }
                    echo "Determined Image Tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Lint & Test Code') {
            steps {
                sh '''
                    echo "Running Lint & Syntax Tests..."
                    # A built-in Python tool that checks for basic syntax errors!
                    python3 -m py_compile main.py
                '''
            }
        }

        stage('Build & Push Docker Image') {
            when {
                anyOf {
                    branch 'staging'
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
        
        stage('Update GitOps Manifests') {
            when {
                anyOf {
                    branch 'staging'
                    buildingTag()
                }
            }
            steps {
                // Ensure you have a GitHub Personal Access Token saved in Jenkins as a 'Username with password' named 'github-credentials'
                withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GITHUB_USER', passwordVariable: 'GITHUB_TOKEN')]) {
                    sh """
                        # Clean up previous runs
                        rm -rf deepdive-gitops

                        # 1. Clone the GitOps Repository
                        git clone https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/bunnywkwk/deepdive-gitops.git
                        cd deepdive-gitops
                        
                        # 2. Update the image tag in the correct environment folder using sed
                        sed -i "s|image: bunnywkwk/argo-deepdive-api:.*|image: ${env.IMAGE}|g" ${env.TARGET_GITOPS_FOLDER}/api/api-deployment.yaml
                        
                        # 3. Commit and Push back to main
                        git config user.email "jenkins@aeron"
                        git config user.name "Jenkins Automation"
                        git add .
                        git commit -m "chore: automate update api image to ${env.IMAGE_TAG} in ${env.TARGET_GITOPS_FOLDER}" || echo "No changes to commit"
                        git push origin main
                    """
                }
            }
        }
    }
}
