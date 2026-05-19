#!/bin/bash
# AWS/GCP Cloud Deployment

set -e

echo "Configuring cloud deployment..."

# AWS ECS
echo "Setting up AWS ECS..."
aws ecr create-repository --repository-name infrarisk --region us-east-1 || true
docker tag infrarisk:v1.0 <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/infrarisk:v1.0
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com
docker push <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/infrarisk:v1.0

# GCP Cloud Run
echo "Setting up GCP Cloud Run..."
gcloud builds submit --tag gcr.io/<PROJECT_ID>/infrarisk:v1.0
gcloud run deploy infrarisk --image gcr.io/<PROJECT_ID>/infrarisk:v1.0 --platform managed --region us-central1 --memory 2Gi

echo "Cloud deployment ready"
