#!/bin/bash

# JornaGEO Deployment Script
DOMAIN_NAME="jornageo.dataiesb.com"
STACK_NAME="jornageo-infrastructure"
REGION="us-east-1"

echo "Deploying JornaGEO Infrastructure..."

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file infrastructure.yaml \
  --stack-name $STACK_NAME \
  --parameter-overrides DomainName=$DOMAIN_NAME \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# Get S3 bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
  --output text \
  --region $REGION)

echo "S3 Bucket: $BUCKET_NAME"

# Upload website files to S3
echo "Uploading website files..."
aws s3 sync . s3://$BUCKET_NAME \
  --exclude "*.sh" \
  --exclude "*.yaml" \
  --exclude "*.py" \
  --exclude ".git/*" \
  --exclude "README.md"

# Get CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text \
  --region $REGION)

# Invalidate CloudFront cache
echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

echo "Deployment completed!"
echo "Website URL: https://$DOMAIN_NAME"
