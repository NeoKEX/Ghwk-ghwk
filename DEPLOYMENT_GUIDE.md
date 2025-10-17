# Deployment Guide - Image Generation API on Render

This guide will help you deploy your image generation service on Render's free tier. The API returns **base64-encoded data URLs** instead of binary data, with no external dependencies required.

## Architecture Overview

Your API uses a **two-tier architecture**:
- **API Service** - Lightweight Flask API that handles requests and returns JSON with base64 data URLs
- **Worker Service** - Heavy service that runs Perchance image generation and encodes to base64

## Prerequisites

Before deploying, you need:
1. A [Render](https://render.com) account (free tier available)
2. A GitHub account to host your code

## Step 1: Prepare Your GitHub Repository

1. Create a new GitHub repository (e.g., `image-generation-api`)
2. Push all your project files to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/image-generation-api.git
   git push -u origin main
   ```

## Step 2: Deploy to Render

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

## Step 3: Configure Environment Variables

### API Service Environment Variables

1. Go to your **image-api** service in Render Dashboard
2. Click **"Environment"** in the left sidebar
3. Add the following environment variable:
   - **Key**: `PERCHANCE_WORKER_URL`
   - **Value**: Your worker URL (e.g., `https://perchance-worker.onrender.com`)
   - To find your worker URL: Go to worker service → Copy the URL at the top
4. Click **"Save Changes"**
5. The service will automatically redeploy

### Worker Service Environment Variables

No environment variables needed for the worker service!

## Step 4: Test Your API

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
  "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
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
  "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "fantasy castle in clouds",
  "seed": 789012,
  "shape": "portrait",
  "guidance_scale": 8.0,
  "negative_prompt": "blurry,low quality"
}
```

**Note**: The `image_url` is a base64-encoded data URL that can be used directly in HTML `<img>` tags or CSS.

## Troubleshooting

### "Worker service not configured" Error
- Ensure `PERCHANCE_WORKER_URL` is set in API service environment variables
- Verify the URL is correct (should start with `https://`)
- Redeploy the API service after setting the variable


### Timeout Errors (504)
- **Normal behavior** on free tier for first request after sleeping
- Service needs 30-60 seconds to wake up
- Subsequent requests will be faster

### Connection Errors (503)
- Check that both services are deployed and running in Render Dashboard
- Verify the worker URL is accessible
- Check Render logs for errors

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

### Base64 Data URLs
- **No external dependencies** - Images encoded directly in JSON responses
- **No rate limits** - No external API calls for storage
- **Larger responses** - Base64 encoding increases response size by ~33%
- **Direct embedding** - Data URLs work directly in browsers

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

- Never commit sensitive data to GitHub
- Use Render's environment variables for configuration
- Base64 data URLs are embedded in responses (no separate image storage)

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
- **Perchance**: [Perchance Text-to-Image](https://perchance.org/text-to-image-plugin)

## Alternative Image Delivery

If you need traditional image URLs instead of base64 data URLs, you can integrate:

- **Imgur**: Free tier with 12,500 requests/day
- **Cloudinary**: Free tier with 25GB storage/bandwidth
- **AWS S3**: Free tier for 12 months (5GB storage)
- **Backblaze B2**: 10GB free storage

Modify the `image_to_base64()` function in `render_worker/worker.py` to upload instead of encode.
