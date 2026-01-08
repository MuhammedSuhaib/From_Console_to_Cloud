#!/bin/bash

# Script to deploy the backend to Hugging Face Spaces

echo "Preparing backend for Hugging Face Spaces deployment..."

# Create a zip file with all necessary files
cd ../..
zip -r backend-hf-deploy.zip backend/

echo "Deployment package created: backend-hf-deploy.zip"

echo "To deploy to Hugging Face Spaces:"
echo "1. Go to https://huggingface.co/spaces"
echo "2. Click 'Create Space'"
echo "3. Select 'Docker' SDK and 'No secrets' (add secrets later in Space settings)"
echo "4. Upload the backend-hf-deploy.zip file or clone this repository"
echo "5. Add the following environment variables in Space settings:"
echo "   - DATABASE_URL (your Neon database URL)"
echo "   - BETTER_AUTH_SECRET (your Better Auth secret)"
echo "   - FASTAPI_ALGORITHM"
echo "   - FASTAPI_ACCESS_TOKEN_EXPIRE_MINUTES"

echo ""
echo "Alternatively, you can use the Hugging Face CLI:"
echo "1. Install: pip install huggingface_hub"
echo "2. Login: huggingface-cli login"
echo "3. Create space: hf_hub create-space your-username/todo-backend -r docker"
echo "4. Upload files to the space repository"