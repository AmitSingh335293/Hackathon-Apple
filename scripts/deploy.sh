#!/bin/bash

# Deployment script for NLP to SQL Analytics System
# This script automates the deployment to AWS ECS Fargate

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPOSITORY_NAME="nlp-sql-analytics"
ECS_CLUSTER_NAME="nlp-sql-cluster"
ECS_SERVICE_NAME="nlp-sql-service"
TASK_FAMILY="nlp-sql-analytics"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI not found. Please install it first."
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
log_info "AWS Account ID: $AWS_ACCOUNT_ID"

# ECR Repository URL
ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPO="${ECR_URL}/${ECR_REPOSITORY_NAME}"

# Step 1: Login to ECR
log_info "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL

# Step 2: Create ECR repository if it doesn't exist
log_info "Checking ECR repository..."
if ! aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION &> /dev/null; then
    log_info "Creating ECR repository..."
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY_NAME \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true
else
    log_info "ECR repository already exists"
fi

# Step 3: Build Docker image
log_info "Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME:latest .

# Step 4: Tag image
log_info "Tagging Docker image..."
docker tag $ECR_REPOSITORY_NAME:latest $ECR_REPO:latest
docker tag $ECR_REPOSITORY_NAME:latest $ECR_REPO:$(date +%Y%m%d-%H%M%S)

# Step 5: Push image to ECR
log_info "Pushing Docker image to ECR..."
docker push $ECR_REPO:latest
docker push $ECR_REPO:$(date +%Y%m%d-%H%M%S)

log_info "Docker image pushed successfully!"

# Step 6: Update task definition with new image
log_info "Updating ECS task definition..."
sed "s|YOUR_ACCOUNT_ID|$AWS_ACCOUNT_ID|g" deployment/ecs-task-definition.json > /tmp/task-def.json

# Register new task definition
NEW_TASK_DEF=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-def.json \
    --region $AWS_REGION \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

log_info "New task definition registered: $NEW_TASK_DEF"

# Step 7: Update ECS service
log_info "Updating ECS service..."
aws ecs update-service \
    --cluster $ECS_CLUSTER_NAME \
    --service $ECS_SERVICE_NAME \
    --task-definition $NEW_TASK_DEF \
    --region $AWS_REGION \
    --force-new-deployment

log_info "ECS service update initiated"

# Step 8: Wait for deployment
log_info "Waiting for service to stabilize..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER_NAME \
    --services $ECS_SERVICE_NAME \
    --region $AWS_REGION

log_info "Deployment completed successfully! ✅"

# Cleanup
rm -f /tmp/task-def.json

log_info "To view service status:"
echo "  aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --region $AWS_REGION"
