# Image Generation API

A Flask-based image generation service that uses Perchance AI text-to-image and returns base64-encoded data URLs. Designed to run on Render's free tier with no external API dependencies.

## Features

- 🎨 **AI Image Generation** - Powered by Perchance text-to-image
- 🔗 **Data URL Responses** - Returns base64-encoded image data URLs
- 🚀 **Free Deployment** - Runs on Render's free tier
- 🌐 **Simple API** - RESTful JSON API with GET requests
- 📦 **No External Dependencies** - No API keys or cloud storage needed

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
  "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
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
2. [GitHub](https://github.com) account

### Quick Deploy Steps

1. **Deploy to Render**
   - Push this repo to GitHub
   - In Render Dashboard: New → Blueprint
   - Connect your GitHub repo
   - Render auto-detects `render.yaml`

2. **Configure Environment Variable**
   - API service: Set `PERCHANCE_WORKER_URL` to your worker URL
   - Worker URL format: `https://perchance-worker.onrender.com`

3. **Done!** Your API is live 🎉

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────┐
│   User      │─────▶│  API Service │─────▶│  Worker  │
│             │      │  (Flask)     │      │ (Docker) │
└─────────────┘      └──────────────┘      └──────────┘
                            │                     │
                            │                     ▼
                            │              ┌──────────────┐
                            │              │   Generate   │
                            │              │  & Encode    │
                            │              │   Base64     │
                            │              └──────────────┘
                            ▼                     │
                     ┌──────────────┐            │
                     │ JSON Response│◀───────────┘
                     │ with Data URL│
                     └──────────────┘
```

### Services

- **API Service**: Lightweight Flask API that handles requests and returns JSON
- **Worker Service**: Heavy-duty Docker container running Perchance image generation
- **Base64 Encoding**: Images encoded as data URLs (no external storage needed)

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
- ✅ No external API keys or services required
- ✅ No credit card required

**Note**: On Render free tier, services sleep after 15 minutes. First request after sleeping takes 30-60 seconds.

## Limitations

### Render Free Tier
- Services sleep after 15 minutes of inactivity
- 512MB RAM per service
- Cold start: 30-60 seconds

### Base64 Data URLs
- Images embedded in JSON response (larger response size)
- Best for small to medium images
- Not cached like traditional image URLs

## Upgrading

For better performance, consider:
- **Render Starter** ($7/month): Always on, no cold starts
- **External Storage** (optional): Add Cloudinary, AWS S3, or Imgur for smaller responses

## Tech Stack

- **Backend**: Flask (Python)
- **Image Generation**: Perchance AI
- **Image Format**: Base64-encoded data URLs
- **Deployment**: Render (Docker + Python)
- **Production Server**: Gunicorn

## Support

- 📖 [Full Deployment Guide](DEPLOYMENT_GUIDE.md)
- 🔧 [Render Documentation](https://render.com/docs)
- 🎨 [Perchance AI](https://perchance.org/text-to-image-plugin)

## License

This project is open source and available for use.

---

**Happy Image Generating! 🎨✨**
