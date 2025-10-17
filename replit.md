# Image Generation API

## Overview

This is a Flask-based image generation service that uses Perchance text-to-image and returns images as base64-encoded data URLs. The service is designed to run on Render's free tier with a two-service architecture and requires no external API keys.

**Current Status**: Ready for Render deployment. Both API and worker services are configured to run on Render's free tier with images returned as base64 data URLs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### API Service (Render)
- **Flask REST API** - Lightweight service that handles incoming requests
- **JSON Responses** - Returns base64-encoded data URLs instead of binary data
- **Stateless Design** - No data persistence; all requests are forwarded to worker
- **Environment-based Configuration** - Worker URL configured via `PERCHANCE_WORKER_URL` environment variable
- **Health Check Endpoint** - Monitors service status and worker connectivity

**Rationale**: Running a minimal API on Render's free tier keeps the service responsive. Returning data URLs instead of binary data is essential for Render's ephemeral storage.

### Worker Service (Render)
- **Dockerized Flask Worker** - Isolated service running Perchance image generation library
- **Base64 Encoding** - Converts generated images to base64 data URLs
- **Async Processing** - Uses asyncio to handle image generation efficiently
- **Independent Deployment** - Separate Docker container allows for scaling and updates without affecting main API

**Rationale**: Perchance library requires specific dependencies (Playwright, Pillow) and compute resources that are better suited for a containerized environment. Base64 encoding eliminates the need for external storage services and API keys.

### Communication Pattern
- **HTTP-based Service-to-Service** - Main API forwards requests to worker via HTTP POST
- **Request Translation** - API converts GET requests (user-facing) to POST requests (worker-facing)
- **JSON Response Flow** - Worker returns base64 image in JSON; API converts to data URL and forwards to user
- **Parameter Forwarding** - Supports prompt, seed, guidance_scale, shape, and negative_prompt parameters

**Alternatives Considered**: 
- Direct binary response - Rejected due to Render's ephemeral storage
- Queue-based async processing - Rejected for simplicity; synchronous HTTP sufficient for current use case
- Local file storage - Rejected because Render free tier has no persistent storage
- External cloud storage - Rejected to avoid API key management and additional dependencies

**Pros**: Clear separation of concerns, easier debugging, independent scaling, no external dependencies
**Cons**: Additional network latency, larger JSON responses due to base64 encoding

### Image Format
- **Base64 Data URLs** - Images encoded as base64 and returned in JSON
- **PNG Format** - Generated images are PNG format
- **Direct Embedding** - Data URLs can be used directly in HTML img tags or CSS
- **No External Storage** - Eliminates need for cloud storage services

**Alternatives Considered**:
- Imgur - Free but requires API key management
- Cloudinary - More features but adds complexity
- AWS S3 - Requires payment info after free tier expires
- Local storage - Not possible on Render free tier (ephemeral)

**Rationale**: Base64 data URLs provide the simplest integration with no API keys or external services required, perfect for a free deployment.

### Image Generation
- **Perchance Library** - Uses `perchance` Python package for AI image generation
- **Shape Options** - Supports portrait, landscape, and square aspect ratios
- **Guidance Scale Control** - Configurable prompt adherence (default: 7.0)
- **Seed Support** - Reproducible results via seed parameter (-1 for random)
- **Negative Prompts** - Allows specifying unwanted elements

### Error Handling
- **Configuration Validation** - Checks worker URL presence before processing
- **Parameter Validation** - Validates required fields and provides clear error messages
- **Network Error Handling** - Gracefully handles timeouts and connection errors to worker
- **Service Status Monitoring** - Health endpoints on both API and worker for monitoring
- **Structured Error Responses** - All errors return JSON with `success: false` and detailed error messages

### File Organization
- **API Service** - Main application files
  - `app.py` - Main Flask API application (returns JSON with base64 data URLs)
  - `requirements.txt` - Python dependencies for API (Flask, requests, gunicorn)
  - `render.yaml` - Render deployment configuration for both services
  - `DEPLOYMENT_GUIDE.md` - Complete deployment instructions for Render
  
- **Render Worker** - Worker service files in `render_worker/` folder
  - `worker.py` - Flask worker that runs Perchance and returns base64 images
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
  - No external API keys or storage services required

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

- **Base64 (built-in)** - Image encoding
  - Converts binary image data to base64 strings
  - No additional dependencies needed

### Environment Configuration

**API Service:**
- **PERCHANCE_WORKER_URL** - Required environment variable pointing to deployed worker
  - Format: `https://your-worker.onrender.com`
  - Used by API to locate and communicate with worker service

**Worker Service:**
- No environment variables required
  - Worker generates and encodes images without external dependencies

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
  "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
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

- **Image Format Change**: Switched from Imgur URLs to base64-encoded data URLs
- **Removed External Dependencies**: Eliminated Imgur API integration and requirements
- **Simplified Setup**: No API keys or external services needed
- **Worker Update**: Modified to return base64 images instead of uploading to cloud storage
- **API Enhancement**: Updated to convert base64 to data URLs for direct browser usage
- **Documentation Update**: Removed all Imgur-related setup instructions
- **Dependencies Cleanup**: Removed requests library from worker requirements

## Deployment Instructions

See `DEPLOYMENT_GUIDE.md` for complete step-by-step instructions to deploy on Render's free tier.

**Quick Steps:**
1. Push code to GitHub
2. Deploy to Render using render.yaml blueprint
3. Set environment variable (PERCHANCE_WORKER_URL for API)
4. Test the API!
