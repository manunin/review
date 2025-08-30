#!/bin/bash

# Script to prepare frontend for AWS Elastic Beanstalk deployment

se# Create ZIP archive from deploy-temp
echo "📦 Creating ZIP archive..."
cd deploy-temp
zip -r ../frontend-deploy.zip . -x "*.DS_Store"
cd ..

# Clean temporary folder
rm -rf deploy-temp

echo "✅ Deployment ready!"
echo "📦 File to upload: frontend-deploy.zip"
echo ""
echo "Deployment instructions:"
echo "1. Go to AWS Elastic Beanstalk console"
echo "2. Select your application"
echo "3. Click 'Upload and Deploy'"
echo "4. Upload the frontend-deploy.zip file"eparing frontend deployment for AWS Elastic Beanstalk..."

# Navigate to frontend directory
cd "$(dirname "$0")"

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf dist
rm -f frontend-deploy.zip

# Temporarily set relative paths for static assets
echo "⚙️  Configuring deployment settings..."
if ! grep -q "base:" vite.config.ts; then
  # Add base: './' to Vite configuration
  sed -i '' 's/export default defineConfig({/export default defineConfig({\
  base: ".\/",/' vite.config.ts
  MODIFIED_VITE=true
else
  MODIFIED_VITE=false
fi

# Build the project
echo "🔨 Building the project..."
npm run build

# Restore original configuration if modified
if [ "$MODIFIED_VITE" = true ]; then
  echo "🔄 Restoring original configuration..."
  sed -i '' '/base: "\.\/",/d' vite.config.ts
fi

# Create ZIP archive with minimal Node.js server for static files
echo "📁 Creating deployment structure..."
mkdir -p deploy-temp/public
cp -r dist/* deploy-temp/public/

# Create minimal package.json for Node.js server
cat > deploy-temp/package.json << 'EOF'
{
  "name": "viewman-frontend-static",
  "version": "1.0.0",
  "description": "Static server for Viewman frontend",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF

# Create simple Express server for static files
cat > deploy-temp/server.js << 'EOF'
const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 8080;

// Serve static files from public folder
app.use(express.static(path.join(__dirname, 'public')));

// For SPA - redirect all unknown routes to index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
EOF

# Create ZIP archive from deploy-temp
echo "📦 Creating ZIP archive..."
cd deploy-temp
zip -r ../frontend-deploy.zip . -x "*.DS_Store"
cd ..