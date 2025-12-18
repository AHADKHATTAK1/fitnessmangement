# Render.com Deployment Guide

## Quick Start

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub account (easier deployment)

### 2. Create PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `gym-manager-db`
3. Database: `gym_manager`
4. User: (auto-generated)
5. Region: **Singapore** (closest to Pakistan)
6. Plan: **Free**
7. Click **"Create Database"**
8. **COPY** the **Internal Database URL** (starts with `postgresql://`)

### 3. Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `AHADKHATTAK1/fitness-mangement1211`
3. Branch: `main`
4. Name: `gym-manager`
5. Region: **Singapore**
6. Runtime: **Docker**
7. Plan: **Free**

### 4. Add Environment Variables
Click **"Environment"** tab and add:

```
DATABASE_URL = [paste the Internal Database URL from step 2]
FLASK_SECRET_KEY = [any random string, e.g., "your-secret-key-12345"]
GOOGLE_CLIENT_ID = [your Google OAuth client ID, if using]
```

### 5. Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Your app will be live at: `https://gym-manager.onrender.com`

## Post-Deployment

### Migrate Data
Run this command locally to migrate your data:
```powershell
$env:DATABASE_URL="[paste External Database URL from Render]"
python migrate_data.py
```

### Custom Domain (Optional)
1. Go to **Settings** → **Custom Domain**
2. Add: `fitnessmanagement.site`
3. Update DNS in Hostinger:
   - Type: CNAME
   - Name: `@` or `www`
   - Value: `gym-manager.onrender.com`

## Troubleshooting

### If build fails:
- Check **Logs** tab
- Verify all environment variables are set
- Ensure GitHub repo is up to date

### If app crashes:
- Check **Logs** → **Runtime Logs**
- Verify DATABASE_URL is correct
- Test database connection

## Support
Render has excellent documentation: https://render.com/docs
