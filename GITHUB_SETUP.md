# GitHub Setup & Deployment Guide

## Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in (or create an account)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in:
   - **Repository name**: `pokemon-adventure-game` (or any name you like)
   - **Description**: "Pokemon-style 2D Pixel Art Game"
   - **Visibility**: Choose **Public** (required for free GitHub Pages)
   - **DO NOT** initialize with README, .gitignore, or license (we'll add files manually)
4. Click **"Create repository"**

## Step 2: Build Your Game for Web

Make sure your game is built:

```bash
.venv/bin/python build_web.py
```

This creates the `build/web/` directory with all the files needed.

## Step 3: Initialize Git (if not already done)

In your project directory:

```bash
cd /Users/catherinehoang/Downloads/cursor-test
git init
```

## Step 4: Create .gitignore

Create a `.gitignore` file to exclude unnecessary files:

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/

# Build outputs
build/
web-build/
*.apk

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
EOF
```

## Step 5: Add and Commit Files

```bash
# Add all files (except those in .gitignore)
git add .

# Commit
git commit -m "Initial commit: Pokemon Adventure Game"
```

## Step 6: Connect to GitHub

1. Copy the repository URL from GitHub (it looks like: `https://github.com/yourusername/pokemon-adventure-game.git`)

2. Add the remote and push:

```bash
# Replace YOUR_USERNAME and REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub username and password (or use a Personal Access Token).

## Step 7: Set Up GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/build/web` (or `/` if you want root)
5. Click **Save**

## Step 8: Access Your Game

After a few minutes, your game will be live at:
```
https://YOUR_USERNAME.github.io/REPO_NAME/
```

Or if you put files in root:
```
https://YOUR_USERNAME.github.io/REPO_NAME/build/web/
```

## Alternative: Deploy Only the Web Build

If you want to deploy ONLY the web build (not the source code):

### Option A: Create a Separate Branch

```bash
# Create a new branch for the web build
git checkout -b gh-pages

# Copy web build files to root
cp -r build/web/* .

# Add and commit
git add .
git commit -m "Deploy web build"

# Push to GitHub
git push origin gh-pages
```

Then in GitHub Settings → Pages, select `gh-pages` branch and `/` folder.

### Option B: Use a Separate Repository

1. Create a new repository just for the web build
2. Copy only `build/web/` contents to that repo
3. Enable Pages on that repository

## Updating Your Game

After making changes:

```bash
# 1. Rebuild
.venv/bin/python build_web.py

# 2. Commit changes
git add .
git commit -m "Update game"

# 3. Push to GitHub
git push
```

GitHub Pages will automatically update (may take 1-2 minutes).

## Troubleshooting

**"Page not found" error:**
- Wait a few minutes for GitHub to build
- Check that the branch/folder is correct in Settings
- Make sure `index.html` is in the root of the selected folder

**Files not updating:**
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check GitHub Actions tab for build errors

**Need to use a custom domain?**
- In GitHub Pages settings, add your custom domain
- Update your domain's DNS with a CNAME record pointing to `YOUR_USERNAME.github.io`

## Quick Reference

```bash
# Initial setup (one time)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main

# After making changes
.venv/bin/python build_web.py  # Rebuild
git add .
git commit -m "Description of changes"
git push
```

