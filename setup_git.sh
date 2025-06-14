#!/bin/bash

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Raspberry Pi Camera Application"

# Instructions for GitHub
echo "To push to GitHub:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Then run these commands (replace with your repository URL):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/camera_app_RasPi.git"
echo "   git branch -M main"
echo "   git push -u origin main" 