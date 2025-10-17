# Deployment Guide - Perchance Image Generation API

This guide will help you deploy your image generation service that uses Perchance text-to-image.

## Architecture Overview

Your API uses a **two-tier architecture**:
- **Replit Flask API** - Lightweight proxy that handles requests (this app)
- **Render Worker** - Heavy service that runs Perchance image generation with Firefox/Playwright

## Step-by-Step Deployment

### 1. Deploy the Worker to Render

#### Option A: Using GitHub (Recommended)

1. **Create a GitHub repository**:
   - Go to [GitHub](https://github.com) and create a new repository
   - Name it something like `perchance-worker`

2. **Upload worker files**:
   - Upload all files from the `render_worker/` folder to your GitHub repo:
     - `worker.py`
     - `requirements.txt`
     - `Dockerfile`
     - `README.md`

3. **Deploy to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **"New +"** → **"Web Service"**
   - Select **"Build and deploy from a Git repository"**
   - Connect your GitHub account and select your repository
   - Configure the service:
     - **Name**: `perchance-worker` (or your choice)
     - **Environment**: **Docker**
     - **Region**: Choose the closest to you
     - **Instance Type**: 
       - **Free** - Service sleeps after 15 min idle (first request will be slow)
       - **Starter ($7/mo)** - Always on, faster responses
   - Click **"Create Web Service"**

4. **Wait for deployment** (5-10 minutes for first build)

#### Option B: Manual Upload to Render

1. Create a `.zip` file with all files from `render_worker/`
2. Use Render's upload feature in dashboard

### 2. Get Your Worker URL

Once deployed, Render gives you a URL like:
```
https://perchance-worker.onrender.com
```

Copy this URL - you'll need it next!

### 3. Configure Replit

1. **Open Secrets** in Replit:
   - Click the lock icon (🔒) in the left sidebar
   - Or go to Tools → Secrets

2. **Add the worker URL**:
   - Key: `PERCHANCE_WORKER_URL`
   - Value: Your Render URL (e.g., `https://perchance-worker.onrender.com`)
   - Click **"Add new secret"**

3. **Restart your Replit app**:
   - Stop and start the workflow
   - Or click the Run button

### 4. Test Your API

Visit your Replit webview or use these endpoints:

#### Check Status
```
GET /
```
Should show `"worker_configured": true`

#### Health Check
```
GET /health
```
Should return `"status": "healthy"`

#### Generate an Image
```
GET /generate?prompt=sunset over mountains&shape=landscape
```

**Note**: If using the free Render tier, the first request after 15 minutes of inactivity will take 30-60 seconds as the service wakes up.

## API Usage

### Generate Image Endpoint

```
GET /generate?prompt=<your prompt>&[optional parameters]
```

**Parameters**:
- `prompt` (required) - Text description of the image
- `seed` (optional) - Number for reproducible results (default: -1 for random)
- `guidance_scale` (optional) - How closely to follow prompt, 0-20 (default: 7.0)
- `shape` (optional) - `portrait`, `landscape`, or `square` (default: square)
- `negative_prompt` (optional) - What to avoid (e.g., "blurry, low quality")

**Example**:
```
/generate?prompt=fantasy castle in clouds&guidance_scale=8&shape=portrait&negative_prompt=blurry
```

## Troubleshooting

### Worker not configured error
- Make sure you set `PERCHANCE_WORKER_URL` in Replit Secrets
- Restart your Replit app after setting the secret

### Timeout errors (504)
- Normal on Render free tier for first request (service waking up)
- If persistent, check Render logs for worker issues

### Connection errors (503)
- Check that your Render worker is deployed and running
- Verify the URL in `PERCHANCE_WORKER_URL` is correct
- Check Render dashboard for worker status

### Worker errors (500)
- Check Render logs in the dashboard
- Verify all dependencies installed correctly
- Ensure Docker build completed successfully

## Cost Information

### Replit
- Free tier available
- Charges may apply for heavy usage

### Render
- **Free tier**: 
  - 750 hours/month free
  - Service sleeps after 15 min idle
  - Slower cold starts
- **Paid tier ($7/mo)**: 
  - Always on
  - No cold starts
  - Better performance

## Next Steps

Once everything works:
1. Consider upgrading Render to paid tier for better performance
2. Add rate limiting if needed
3. Deploy your Replit app for public access (click Deploy button)
4. Share your API with others!

## Support

- **Render issues**: Check [Render docs](https://render.com/docs)
- **Perchance issues**: See [Perchance documentation](https://perchance.org/text-to-image-plugin)
