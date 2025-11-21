# GitHub Setup Guide for TimeTree Home Assistant Integration

This guide will walk you through getting your TimeTree Home Assistant integration project on GitHub.

## Prerequisites

You'll need:
- A GitHub account (create one at https://github.com if you don't have one)
- Git installed on your computer

## Step 1: Install Git (if not already installed)

Since Git is not currently installed on your system, you'll need to install it first:

1. Download Git for Windows from: https://git-scm.com/download/win
2. Run the installer with default settings
3. After installation, restart your terminal/PowerShell

To verify Git is installed, open PowerShell and run:
```powershell
git --version
```

## Step 2: Configure Git (First-time setup)

Open PowerShell and configure your Git identity:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace "Your Name" and "your.email@example.com" with your actual name and email.

## Step 3: Initialize Git Repository

Navigate to your project directory and initialize Git:

```powershell
cd c:\Users\id947280\dev\TTHA
git init
```

## Step 4: Add Files to Git

Add all your project files to Git:

```powershell
git add .
```

Check what will be committed:

```powershell
git status
```

## Step 5: Create Initial Commit

Commit your files:

```powershell
git commit -m "Initial commit: TimeTree Home Assistant integration"
```

## Step 6: Create GitHub Repository

1. Go to https://github.com
2. Log in to your account
3. Click the "+" icon in the top-right corner
4. Select "New repository"
5. Fill in the repository details:
   - **Repository name**: `timetree-homeassistant` (or your preferred name)
   - **Description**: "Custom Home Assistant integration for TimeTree calendar synchronization"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 7: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/timetree-homeassistant.git

# Rename the default branch to main (if needed)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

**Important**: Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 8: Verify Upload

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/timetree-homeassistant`
2. You should see all your files including:
   - `README.md`
   - `custom_components/timetree/` directory
   - `LICENSE`
   - `.gitignore`

## Alternative: Using GitHub Desktop (Easier for Beginners)

If you prefer a graphical interface:

1. Download GitHub Desktop from: https://desktop.github.com
2. Install and sign in with your GitHub account
3. Click "Add" → "Add Existing Repository"
4. Browse to `c:\Users\id947280\dev\TTHA`
5. Click "Publish repository" button
6. Choose repository name and visibility
7. Click "Publish repository"

## Future Updates

When you make changes to your code:

```powershell
# Check what changed
git status

# Add changed files
git add .

# Commit changes
git commit -m "Description of what you changed"

# Push to GitHub
git push
```

## Troubleshooting

### Authentication Issues

If you get authentication errors when pushing:
- GitHub no longer accepts password authentication
- You'll need to use a Personal Access Token (PAT) or SSH key
- See: https://docs.github.com/en/authentication

### Quick PAT Setup:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy the token
4. When Git asks for password, paste the token instead

## Next Steps

After uploading to GitHub:
1. Add topics/tags to your repository (e.g., "home-assistant", "timetree", "calendar")
2. Consider adding a screenshot to the README
3. Add installation instructions for HACS (Home Assistant Community Store) if desired
4. Share your repository with the Home Assistant community!

## Need Help?

If you encounter any issues:
1. Check the error message carefully
2. Search for the error on Google or GitHub
3. Ask in Home Assistant community forums
4. Feel free to ask me for help!
