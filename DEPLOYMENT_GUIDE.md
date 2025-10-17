# Deployment Guide - Image Generation API on Render

This guide will help you deploy your image generation service on Render's free tier. The API returns **image URLs** instead of binary data, making it perfect for Render's ephemeral storage.

## Architecture Overview

Your API uses a **two-tier architecture**:
- **API Service** - Lightweight Flask API that handles requests and returns JSON with image URLs
- **Worker Service** - Heavy service that runs Perchance image generation and uploads to Imgur

## Prerequisites

Before deploying, you need:
1. A [Render](https://render.com) account (free tier available)
2. An [Imgur](https://imgur.com) account for image storage (free)
3. A GitHub account to host your code

## Step 1: Get Imgur API Credentials

Images are stored on Imgur (free tier) since Render's free tier has ephemeral storage.

1. Go to [Imgur API Registration](https://api.imgur.com/oauth2/addclient)
2. Log in or create an Imgur account
3. Fill out the registration form:
   - **Application name**: Image Generation API (or your choice)
   - **Authorization type**: Select "OAuth 2 authorization without a callback URL"
   - **Email**: Your email address
   - **Description**: Image generation service
4. Click **Submit**
5. **Copy your Client ID** - you'll need this later

## Step 2: Prepare Your GitHub Repository

1. Create a new GitHub repository (e.g., `image-generation-api`)
2. Push all your project files to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/image-generation-api.git
   git push -u origin main
   ```

## Step 3: Deploy to Render

### Option A: Using render.yaml (Recommended)

The `render.yaml` file automatically deploys both services.

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect the `render.yaml` and show two services:
   - **image-api** (API Service)
   - **perchance-worker** (Worker Service)
5. Click **"Apply"**

### Option B: Manual Deployment

#### Deploy Worker Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `perchance-worker`
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: `render_worker`
   - **Environment**: **Docker**
   - **Docker Context**: `render_worker`
   - **Dockerfile Path**: `render_worker/Dockerfile`
   - **Instance Type**: **Free**
4. Click **"Create Web Service"**
5. Wait for deployment (5-10 minutes for first build)

#### Deploy API Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `image-api`
   - **Region**: Same as worker
   - **Branch**: `main`
   - **Root Directory**: Leave empty (root)
   - **Environment**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: **Free**
4. Click **"Create Web Service"**

## Step 4: Configure Environment Variables

### Worker Service Environment Variables

1. Go to your **perchance-worker** service in Render Dashboard
2. Click **"Environment"** in the left sidebar
3. Add the following environment variable:
   - **Key**: `IMGUR_CLIENT_ID`
   - **Value**: Your Imgur Client ID from Step 1
4. Click **"Save Changes"**
5. The service will automatically redeploy

### API Service Environment Variables

1. Go to your **image-api** service in Render Dashboard
2. Click **"Environment"** in the left sidebar
3. Add the following environment variable:
   - **Key**: `PERCHANCE_WORKER_URL`
   - **Value**: Your worker URL (e.g., `https://perchance-worker.onrender.com`)
   - To find your worker URL: Go to worker service → Copy the URL at the top
4. Click **"Save Changes"**
5. The service will automatically redeploy

## Step 5: Test Your API

Once both services are deployed and configured:

### Get Your API URL

Your API URL will be something like:
```
https://image-api.onrender.com
```

### Test Endpoints

#### 1. Check API Documentation
```
GET https://image-api.onrender.com/
```

#### 2. Health Check
```
GET https://image-api.onrender.com/health
```
Should return: `{"status": "healthy", "worker_configured": true}`

#### 3. Generate an Image
```
GET https://image-api.onrender.com/generate?prompt=sunset over mountains&shape=landscape
```

**Response:**
```json
{
  "success": true,
  "image_url": "https://i.imgur.com/xxxxx.png",
  "prompt": "sunset over mountains",
  "seed": 123456,
  "shape": "landscape",
  "guidance_scale": 7.0
}
```

**Note**: On Render free tier, services sleep after 15 minutes of inactivity. The first request after sleeping will take 30-60 seconds as the service wakes up.

## API Usage

### Generate Image Endpoint

```
GET /generate?prompt=<text>&[optional parameters]
```

**Required Parameters:**
- `prompt` - Text description of the image

**Optional Parameters:**
- `seed` - Number for reproducible results (default: -1 for random)
- `guidance_scale` - How closely to follow prompt, 0-20 (default: 7.0)
- `shape` - `portrait`, `landscape`, or `square` (default: `square`)
- `negative_prompt` - What to avoid in the image

**Example:**
```
/generate?prompt=fantasy castle in clouds&guidance_scale=8&shape=portrait&negative_prompt=blurry,low quality
```

**Response Format:**
```json
{
  "success": true,
  "image_url": "https://i.imgur.com/xxxxx.png",
  "prompt": "fantasy castle in clouds",
  "seed": 789012,
  "shape": "portrait",
  "guidance_scale": 8.0,
  "negative_prompt": "blurry,low quality"
}
```

## Troubleshooting

### "Worker service not configured" Error
- Ensure `PERCHANCE_WORKER_URL` is set in API service environment variables
- Verify the URL is correct (should start with `https://`)
- Redeploy the API service after setting the variable

### "IMGUR_CLIENT_ID not configured" Error
- Ensure `IMGUR_CLIENT_ID` is set in worker service environment variables
- Verify the Client ID is correct (copy-paste from Imgur)
- Redeploy the worker service after setting the variable

### Timeout Errors (504)
- **Normal behavior** on free tier for first request after sleeping
- Service needs 30-60 seconds to wake up
- Subsequent requests will be faster

### Connection Errors (503)
- Check that both services are deployed and running in Render Dashboard
- Verify the worker URL is accessible
- Check Render logs for errors

### Imgur Upload Errors
- Verify your Imgur Client ID is valid
- Check Imgur API rate limits (free tier: 12,500 requests/day)
- View worker service logs in Render for details

### Image Generation Errors
- Check worker service logs in Render Dashboard
- Ensure Docker build completed successfully
- Verify all dependencies installed correctly

## Cost Information

### Render Free Tier
- **750 hours/month** per service (enough for 2 services always on)
- Services **sleep after 15 minutes** of inactivity
- **Cold start**: 30-60 seconds when waking up
- Limited to **512MB RAM** per service

### Imgur Free Tier
- **12,500 API requests/day**
- Unlimited image storage
- No bandwidth limits
- Images never expire

### Upgrading (Optional)

If you need better performance:
- **Render Starter Plan ($7/month per service)**:
  - Always on (no sleeping)
  - No cold starts
  - Better performance
  - More RAM

## Project Structure

```
.
├── app.py                      # Main API service
├── requirements.txt            # API dependencies
├── render.yaml                 # Render deployment config
├── render_worker/
│   ├── worker.py              # Worker service
│   ├── requirements.txt       # Worker dependencies
│   ├── Dockerfile             # Docker config
│   └── README.md
├── DEPLOYMENT_GUIDE.md        # This file
└── replit.md                  # Project documentation
```

## Security Notes

- Never commit API keys to GitHub
- Use Render's environment variables for all secrets
- Imgur Client ID is safe to use (Client Secret not needed for uploads)
- Images uploaded to Imgur are publicly accessible

## Next Steps

1. ✅ Test your API with different prompts
2. ✅ Share your API URL with others
3. Consider adding:
   - Rate limiting
   - Authentication
   - Custom domain
   - Monitoring/analytics

## Support

- **Render Issues**: [Render Docs](https://render.com/docs)
- **Imgur API**: [Imgur API Docs](https://apidocs.imgur.com/)
- **Perchance**: [Perchance Text-to-Image](https://perchance.org/text-to-image-plugin)

## Alternative Cloud Storage

If you want to use a different storage provider instead of Imgur:

- **Cloudinary**: Free tier with 25GB storage/bandwidth
- **AWS S3**: Free tier for 12 months (5GB storage)
- **Backblaze B2**: 10GB free storage
- **Supabase Storage**: 1GB free storage

Update the `upload_to_imgur()` function in `render_worker/worker.py` to use your preferred storage.
