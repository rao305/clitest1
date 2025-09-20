#!/bin/bash
# GitHub Setup Script for BoilerAI

echo "🚀 Setting up BoilerAI on GitHub..."

# Check if git is configured
if ! git config user.name > /dev/null 2>&1; then
    echo "❌ Git not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Create a new GitHub repository (you'll need to do this manually)
echo "📝 Please create a new repository on GitHub first:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: boilerai-purdue-advisor"
echo "3. Description: AI-Powered Purdue CS Academic Advisor"
echo "4. Make it Public or Private (your choice)"
echo "5. Don't initialize with README (we already have one)"
echo ""
echo "Press Enter after creating the repository..."

# Wait for user input
read -p "Press Enter to continue..."

# Get repository URL from user
echo ""
echo "📋 Please provide your GitHub repository URL:"
echo "Format: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
read -p "Repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ No repository URL provided. Exiting."
    exit 1
fi

# Add remote and push
echo "🔗 Adding remote repository..."
git remote add origin "$REPO_URL"

echo "🌿 Setting main branch..."
git branch -M main

echo "📤 Pushing to GitHub..."
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Your repository is now available at: $REPO_URL"
echo ""
echo "🎉 BoilerAI is now live on GitHub!"
echo "📚 Complete documentation is in README.md"
echo "🚀 Run 'python universal_purdue_advisor.py' to start the AI advisor"
