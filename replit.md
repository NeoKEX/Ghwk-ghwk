# Image Generation API

## Overview

This is a Flask-based image generation service that uses Perchance text-to-image and returns image URLs hosted on Imgur. The service is designed to run on Render's free tier with a two-service architecture.

**Current Status**: Ready for Render deployment. Both API and worker services are configured to run on Render's free tier with image URLs stored on Imgur.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### API Service (Render)
- **Flask REST API** - Lightweight service that handles incoming requests
- **JSON Responses** - Returns image URLs instead of binary data
- **Stateless Design** - No data persistence; all requests are forwarded to worker
- **Environment-based Configuration** - Worker URL configured via `PERCHANCE_WORKER_URL` environment variable
- **Health Check Endpoint** - Monitors service status and worker connectivity

**Rationale**: Running a minimal API on Render's free tier keeps the service responsive. Returning URLs instead of binary data is essential for Render's ephemeral storage.

### Worker Service (Render)
- **Dockerized Flask Worker** - Isolated service running Perchance image generation library
- **Imgur Integration** - Uploads generated images to Imgur cloud storage
- **Async Processing** - Uses asyncio to handle image generation efficiently
- **Independent Deployment** - Separate Docker container allows for scaling and updates without affecting main API

**Rationale**: Perchance library requires specific dependencies (Playwright, Pillow) and compute resources that are better suited for a containerized environment. Imgur provides free, permanent image hosting which solves Render's ephemeral storage limitation.

### Communication Pattern
- **HTTP-based Service-to-Service** - Main API forwards requests to worker via HTTP POST
- **Request Translation** - API converts GET requests (user-facing) to POST requests (worker-facing)
- **JSON Response Flow** - Worker returns image URL in JSON; API forwards to user
- **Parameter Forwarding** - Supports prompt, seed, guidance_scale, shape, and negative_prompt parameters

**Alternatives Considered**: 
- Direct binary response - Rejected due to Render's ephemeral storage
- Queue-based async processing - Rejected for simplicity; synchronous HTTP sufficient for current use case
- Local file storage - Rejected because Render free tier has no persistent storage

**Pros**: Clear separation of concerns, easier debugging, independent scaling, permanent image URLs
**Cons**: Additional network latency, requires managing two services and Imgur API key

### Image Storage
- **Imgur Cloud Storage** - Free tier with 12,500 requests/day and unlimited storage
- **Base64 Upload** - Images uploaded as base64-encoded data via Imgur API
- **Permanent URLs** - Images never expire and are publicly accessible
- **No Authentication Required** - Only Client ID needed (no Client Secret)

**Alternatives Considered**:
- Cloudinary - More features but adds complexity
- AWS S3 - Requires payment info after free tier expires
- Local storage - Not possible on Render free tier (ephemeral)

**Rationale**: Imgur provides the simplest integration with generous free tier and permanent storage, perfect for a free deployment.

### Image Generation
- **Perchance Library** - Uses `perchance` Python package for AI image generation
- **Shape Options** - Supports portrait, landscape, and square aspect ratios
- **Guidance Scale Control** - Configurable prompt adherence (default: 7.0)
- **Seed Support** - Reproducible results via seed parameter (-1 for random)
- **Negative Prompts** - Allows specifying unwanted elements

### Error Handling
- **Configuration Validation** - Checks worker URL and Imgur Client ID presence before processing
- **Parameter Validation** - Validates required fields and provides clear error messages
- **Network Error Handling** - Gracefully handles timeouts and connection errors to worker
- **Service Status Monitoring** - Health endpoints on both API and worker for monitoring
- **Structured Error Responses** - All errors return JSON with `success: false` and detailed error messages

### File Organization
- **API Service** - Main application files
  - `app.py` - Main Flask API application (returns JSON with image URLs)
  - `requirements.txt` - Python dependencies for API (Flask, requests, gunicorn)
  - `render.yaml` - Render deployment configuration for both services
  - `DEPLOYMENT_GUIDE.md` - Complete deployment instructions for Render
  
- **Render Worker** - Worker service files in `render_worker/` folder
  - `worker.py` - Flask worker that runs Perchance and uploads to Imgur
  - `requirements.txt` - Python dependencies for Docker container
  - `Dockerfile` - Container configuration with Firefox/Playwright
  - `README.md` - Worker-specific documentation

## External Dependencies

### Third-Party Services
- **Render** - Hosting platform for both API and worker services
  - Provides Docker container runtime for worker
  - Python runtime for API
  - Free tier: 750 hours/month per service
  - Services sleep after 15 minutes of inactivity

- **Imgur** - Image hosting and storage
  - Free tier: 12,500 requests/day, unlimited storage
  - No expiration on uploaded images
  - Public image URLs

### Python Libraries

**API Service:**
- **Flask (3.0.3)** - Web framework for API
  - Chosen for simplicity and lightweight footprint
  
- **Requests (2.31.0)** - HTTP client library
  - Used for service-to-service communication with worker
  
- **Gunicorn (21.2.0)** - Production WSGI server
  - Required for running Flask on Render

**Worker Service:**
- **Flask (3.0.3)** - Web framework for worker
  - Chosen for simplicity and lightweight footprint
  
- **Perchance (latest)** - AI image generation library
  - Core functionality for image creation
  - Requires async/await pattern
  - Currently version 0.0.1 on PyPI
  
- **Pillow (10.4.0)** - Image processing library
  - Required by Perchance for image manipulation
  
- **Playwright (1.48.0)** - Browser automation
  - Required by Perchance for certain generation features
  
- **Requests (2.31.0)** - HTTP client library
  - Used for uploading images to Imgur API

### Environment Configuration

**API Service:**
- **PERCHANCE_WORKER_URL** - Required environment variable pointing to deployed worker
  - Format: `https://your-worker.onrender.com`
  - Used by API to locate and communicate with worker service

**Worker Service:**
- **IMGUR_CLIENT_ID** - Required environment variable for Imgur API
  - Obtained from https://api.imgur.com/oauth2/addclient
  - Used to authenticate Imgur uploads
  - Free tier allows 12,500 requests/day

### Deployment Architecture
- **Render (Both Services)** - Complete hosting on Render free tier
  - API: Python runtime with gunicorn
  - Worker: Docker-based deployment with full Perchance dependencies
  - Auto-deploy from GitHub repository
  - Separate environment variables for each service
  - Blueprint deployment via render.yaml for both services

## API Response Format

### Success Response
```json
{
  "success": true,
  "image_url": "https://i.imgur.com/xxxxx.png",
  "prompt": "sunset over mountains",
  "seed": 123456,
  "shape": "landscape",
  "guidance_scale": 7.0,
  "negative_prompt": "blurry"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error type",
  "details": "Detailed error message"
}
```

## Recent Changes (October 17, 2025)

- **Architecture Migration**: Moved from Replit+Render hybrid to full Render deployment
- **Response Format**: Changed from binary PNG to JSON with image URLs
- **Image Storage**: Integrated Imgur for permanent cloud storage
- **Worker Enhancement**: Added Imgur upload functionality to worker service
- **API Update**: Modified to return JSON responses instead of binary images
- **Deployment Simplification**: Created render.yaml for one-click deployment of both services
- **Documentation**: Completely rewrote DEPLOYMENT_GUIDE.md for Render-only setup
- **Dependencies**: Added gunicorn for production API serving

## Deployment Instructions

See `DEPLOYMENT_GUIDE.md` for complete step-by-step instructions to deploy on Render's free tier.

**Quick Steps:**
1. Get Imgur Client ID from https://api.imgur.com/oauth2/addclient
2. Push code to GitHub
3. Deploy to Render using render.yaml blueprint
4. Set environment variables (IMGUR_CLIENT_ID for worker, PERCHANCE_WORKER_URL for API)
5. Test the API!
