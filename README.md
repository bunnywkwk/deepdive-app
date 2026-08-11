# Argo Deep Dive: Application Repository (CI)

This repository contains the **Source Code** and the **Continuous Integration (CI)** pipeline. 

## What happens here?
This is where developers work. They write Python code and push it to this repository. This repository knows nothing about Kubernetes. Its only job is to build the application and package it into a Docker container.

## The Pipeline (`Jenkinsfile`)
When a developer pushes to this repository, a GitHub Webhook triggers our Jenkins server to start a pipeline:
1. **Lint & Test**: Checks the Python code for syntax errors.
2. **Build & Push**: Builds a Docker image using the `Dockerfile` and pushes it to Docker Hub.
3. **Update GitOps**: Jenkins automatically clones the `deepdive-gitops` repository, edits the YAML files to point to the brand new Docker image tag, and pushes the change back to GitHub!
