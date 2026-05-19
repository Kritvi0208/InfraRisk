#!/bin/bash
# Deploy to Kubernetes

set -e

echo "Building Docker image..."
docker build -t infrarisk:v1.0 .

echo "Pushing to registry..."
docker tag infrarisk:v1.0 kritvi0208/infrarisk:v1.0
docker push kritvi0208/infrarisk:v1.0

echo "Creating K8s deployment..."
kubectl create namespace infrarisk || true

cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: infrarisk-api
  namespace: infrarisk
spec:
  replicas: 3
  selector:
    matchLabels:
      app: infrarisk
  template:
    metadata:
      labels:
        app: infrarisk
    spec:
      containers:
      - name: api
        image: kritvi0208/infrarisk:v1.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: infrarisk-service
  namespace: infrarisk
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: infrarisk
EOF

echo "Deployment complete. Access at: http://localhost"
