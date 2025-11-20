# Deployment Guide - Render

This guide explains how to deploy the Analysis Dashboard to Render.

## Prerequisites

1. GitHub account with repository access
2. Render account (sign up at https://render.com)
3. Redash API credentials

## Step 1: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit: Analysis Dashboard"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/saurabh-cashify/pddAnalysisDashboard.git

# Push to main branch
git push -u origin main
```

## Step 2: Deploy on Render

### 2.1 Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select repository: `saurabh-cashify/pddAnalysisDashboard`

### 2.2 Configure Service

**Basic Settings:**
- **Name**: `pdd-analysis-dashboard` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: (leave empty, root is fine)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

**Environment Variables:**
Add these in the Render dashboard under "Environment":

| Key | Value | Notes |
|-----|-------|-------|
| `REDASH_API_KEY` | `IY2HlHUAz3ZX0Y1p2rg4vaFciUOV0MIlkJT0eyOe` | Your Redash API key (mark as Secret) |
| `REDASH_QUERY_ID` | `4261` | Redash query ID |
| `REDASH_BASE_URL` | `http://redash.prv.api.cashify.in` | Redash base URL |
| `REDASH_MODE` | `qc_automation` | Redash mode |
| `PYTHON_VERSION` | `3.11.0` | Python version (optional, specified in runtime.txt) |

**Important**: Mark `REDASH_API_KEY` as **Secret** in Render dashboard.

### 2.3 Advanced Settings (Optional)

- **Auto-Deploy**: `Yes` (deploys on every push to main)
- **Health Check Path**: Leave empty (or use `/` if needed)

### 2.4 Deploy

Click **"Create Web Service"** and wait for deployment to complete.

## Step 3: Verify Deployment

1. Once deployed, Render will provide a URL like: `https://pdd-analysis-dashboard.onrender.com`
2. Open the URL in your browser
3. Test the dashboard functionality

## Troubleshooting

### Build Fails

- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python version matches `runtime.txt`

### App Crashes on Start

- Check runtime logs in Render dashboard
- Verify all environment variables are set
- Ensure `PORT` environment variable is available (Render sets this automatically)

### Cannot Access Redash API

- Verify `REDASH_BASE_URL` is accessible from Render's servers
- If using internal URL (`redash.prv.api.cashify.in`), you may need:
  - VPN setup
  - Proxy configuration
  - Or use public Redash URL if available

### File Upload Issues

- Render has ephemeral filesystem - uploaded files are lost on restart
- Consider using external storage (S3, etc.) for persistent file storage
- Generated reports are downloaded as ZIP, so they're fine

## Environment Variables Reference

All environment variables have fallback defaults for local development:

- `REDASH_API_KEY`: Redash API key (required in production)
- `REDASH_QUERY_ID`: Redash query ID (default: 4261)
- `REDASH_BASE_URL`: Redash base URL (default: http://redash.prv.api.cashify.in)
- `REDASH_MODE`: Redash mode (default: qc_automation)
- `PORT`: Server port (automatically set by Render, default: 8050 for local)
- `HOST`: Server host (automatically set by Render, default: 0.0.0.0)

## Local Development

For local development, you can create a `.env` file (not committed to git):

```bash
REDASH_API_KEY=your_api_key_here
REDASH_QUERY_ID=4261
REDASH_BASE_URL=http://redash.prv.api.cashify.in
REDASH_MODE=qc_automation
```

Then run:
```bash
python app.py
```

## Updating Deployment

Simply push to the `main` branch and Render will auto-deploy (if auto-deploy is enabled):

```bash
git add .
git commit -m "Your update message"
git push origin main
```

## Support

For issues:
1. Check Render logs
2. Check application logs
3. Verify environment variables
4. Test locally first

