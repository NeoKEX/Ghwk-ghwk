# Perchance Worker for Render

This is a worker service that runs the Perchance image generation library on Render.

## How to Deploy to Render

1. **Create a GitHub Repository** (if you haven't already):
   - Go to GitHub and create a new repository
   - Upload these files from the `render_worker` folder:
     - `worker.py`
     - `requirements.txt`
     - `Dockerfile`

2. **Deploy to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `perchance-worker` (or any name you prefer)
     - **Environment**: Docker
     - **Region**: Choose closest to you
     - **Instance Type**: Free (or paid for better performance)
   - Click "Create Web Service"

3. **Get Your Worker URL**:
   - Once deployed, Render will give you a URL like: `https://perchance-worker.onrender.com`
   - Copy this URL - you'll need it for your Replit app

4. **Configure Your Replit App**:
   - In Replit, set the environment variable:
     ```
     PERCHANCE_WORKER_URL=https://your-worker.onrender.com
     ```

## API Endpoints

### POST /generate
Generate an image from a text prompt.

**Request Body:**
```json
{
  "prompt": "fantasy landscape",
  "seed": -1,
  "guidance_scale": 7.0,
  "shape": "square",
  "negative_prompt": "blurry, low quality"
}
```

**Response:** PNG image file

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Perchance Worker",
  "version": "1.0.0"
}
```

## Notes

- **Free Tier**: Render's free tier spins down after 15 minutes of inactivity, so the first request after idle will be slow (30-60 seconds)
- **Paid Tier**: $7/month for always-on service with faster response times
- The worker uses Playwright to automate Firefox, which needs the GTK libraries installed via the Dockerfile
