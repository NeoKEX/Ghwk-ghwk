# Image Generation API

A Flask-based image generation service that uses Perchance AI text-to-image and returns hosted image URLs. Designed to run on Render's free tier.

## Features

- 🎨 **AI Image Generation** - Powered by Perchance text-to-image
- 🔗 **URL Responses** - Returns image URLs instead of binary data
- ☁️ **Cloud Storage** - Images hosted on Imgur (free, permanent)
- 🚀 **Free Deployment** - Runs on Render's free tier
- 🌐 **Simple API** - RESTful JSON API with GET requests

## Quick Start

### API Usage

Generate an image:
```
GET https://your-api.onrender.com/generate?prompt=sunset%20over%20mountains
```

Response:
```json
{
  "success": true,
  "image_url": "https://i.imgur.com/xxxxx.png",
  "prompt": "sunset over mountains",
  "seed": 123456,
  "shape": "square",
  "guidance_scale": 7.0
}
```

### Parameters

- `prompt` (required) - Text description of the image
- `seed` (optional) - Random seed for reproducibility (default: -1)
- `guidance_scale` (optional) - Prompt adherence 0-20 (default: 7.0)
- `shape` (optional) - `portrait`, `landscape`, or `square` (default: `square`)
- `negative_prompt` (optional) - What to avoid in the image

### Example Requests

```bash
# Basic image generation
curl "https://your-api.onrender.com/generate?prompt=cat+wearing+sunglasses"

# With all parameters
curl "https://your-api.onrender.com/generate?prompt=fantasy+castle&shape=landscape&guidance_scale=8&negative_prompt=blurry"

# Reproducible generation (same seed = same image)
curl "https://your-api.onrender.com/generate?prompt=robot&seed=12345"
```

## Deployment

**Full deployment guide**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Prerequisites

1. [Render](https://render.com) account (free)
2. [Imgur](https://imgur.com) account (free)
3. [GitHub](https://github.com) account

### Quick Deploy Steps

1. **Get Imgur Client ID**
   - Go to https://api.imgur.com/oauth2/addclient
   - Register your application
   - Copy the Client ID

2. **Deploy to Render**
   - Push this repo to GitHub
   - In Render Dashboard: New → Blueprint
   - Connect your GitHub repo
   - Render auto-detects `render.yaml`

3. **Configure Environment Variables**
   - Worker service: Set `IMGUR_CLIENT_ID`
   - API service: Set `PERCHANCE_WORKER_URL`

4. **Done!** Your API is live 🎉

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────┐
│   User      │─────▶│  API Service │─────▶│  Worker  │
│             │      │  (Flask)     │      │ (Docker) │
└─────────────┘      └──────────────┘      └──────────┘
                            │                     │
                            │                     ▼
                            │              ┌──────────┐
                            │              │  Imgur   │
                            │              │  Upload  │
                            │              └──────────┘
                            ▼                     │
                     ┌──────────────┐            │
                     │ JSON Response│◀───────────┘
                     │ with URL     │
                     └──────────────┘
```

### Services

- **API Service**: Lightweight Flask API that handles requests and returns JSON
- **Worker Service**: Heavy-duty Docker container running Perchance image generation
- **Imgur Storage**: Free cloud storage for generated images

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
├── DEPLOYMENT_GUIDE.md        # Full deployment guide
└── README.md                  # This file
```

## API Endpoints

### `GET /`
API documentation and status

### `GET /health`
Health check endpoint

### `GET /generate`
Generate an image from a text prompt

## Cost

**100% Free Setup:**
- ✅ Render Free Tier: 750 hours/month (enough for 2 services)
- ✅ Imgur Free Tier: 12,500 requests/day, unlimited storage
- ✅ No credit card required

**Note**: On Render free tier, services sleep after 15 minutes. First request after sleeping takes 30-60 seconds.

## Limitations

### Render Free Tier
- Services sleep after 15 minutes of inactivity
- 512MB RAM per service
- Cold start: 30-60 seconds

### Imgur Free Tier
- 12,500 API requests per day
- Images are publicly accessible
- No image deletion after upload

## Upgrading

For better performance, consider:
- **Render Starter** ($7/month): Always on, no cold starts
- **Alternative Storage**: Cloudinary, AWS S3, or Backblaze B2

## Tech Stack

- **Backend**: Flask (Python)
- **Image Generation**: Perchance AI
- **Image Storage**: Imgur
- **Deployment**: Render (Docker + Python)
- **Production Server**: Gunicorn

## Support

- 📖 [Full Deployment Guide](DEPLOYMENT_GUIDE.md)
- 🔧 [Render Documentation](https://render.com/docs)
- 🎨 [Perchance AI](https://perchance.org/text-to-image-plugin)
- 📷 [Imgur API](https://apidocs.imgur.com/)

## License

This project is open source and available for use.

---

**Happy Image Generating! 🎨✨**
