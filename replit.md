# Image Generation API

## Overview

This is a Flask-based image generation service that acts as a proxy API for the Perchance text-to-image service. The architecture follows a distributed microservices pattern where the main API (running on Replit) delegates compute-intensive image generation tasks to a separate worker service (deployed on Render). This separation allows the lightweight API to run on Replit while offloading heavy processing to a dedicated worker environment that supports the full Perchance library and its dependencies.

**Current Status**: Ready for deployment. The Replit API is configured to call a Render worker service. Follow DEPLOYMENT_GUIDE.md to deploy the worker and complete setup.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend/API Layer (Replit)
- **Flask-based REST API** - Lightweight proxy service that handles incoming requests
- **Stateless Design** - No data persistence; all requests are forwarded to worker
- **Environment-based Configuration** - Worker URL configured via `PERCHANCE_WORKER_URL` environment variable
- **Health Check Endpoint** - Monitors service status and worker connectivity

**Rationale**: Running a minimal API on Replit keeps the service responsive and within platform constraints, while delegating compute-heavy operations to a dedicated worker.

### Worker Service (Render)
- **Dockerized Flask Worker** - Isolated service running Perchance image generation library
- **Async Processing** - Uses asyncio to handle image generation efficiently
- **Independent Deployment** - Separate codebase allows for scaling and updates without affecting main API

**Rationale**: Perchance library requires specific dependencies (Playwright, Pillow) and compute resources that are better suited for a containerized environment like Render. This separation of concerns allows each service to be optimized for its specific role.

### Communication Pattern
- **HTTP-based Service-to-Service** - Main API forwards requests to worker via HTTP POST
- **Request Translation** - API converts GET requests (user-facing) to POST requests (worker-facing)
- **Parameter Forwarding** - Supports prompt, seed, guidance_scale, shape, and negative_prompt parameters

**Alternatives Considered**: 
- Direct integration of Perchance in Replit - Rejected due to dependency and resource constraints
- Queue-based async processing - Rejected for simplicity; synchronous HTTP sufficient for current use case

**Pros**: Clear separation of concerns, easier debugging, independent scaling
**Cons**: Additional network latency, requires managing two services

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

### File Organization
- **Replit API** - Main application files
  - `app.py` - Main Flask API application
  - `pyproject.toml` - Python dependencies for Replit
  - `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
  
- **Render Worker** - Worker service files in `render_worker/` folder
  - `worker.py` - Flask worker that runs Perchance image generation
  - `requirements.txt` - Python dependencies for Docker container
  - `Dockerfile` - Container configuration with Firefox/Playwright
  - `README.md` - Worker-specific documentation

## External Dependencies

### Third-Party Services
- **Render** - Hosting platform for worker service
  - Provides Docker container runtime
  - Handles worker service deployment and scaling
  - Free tier available for development

### Python Libraries
- **Flask (3.0.3)** - Web framework for both API and worker
  - Chosen for simplicity and lightweight footprint
  
- **Perchance (1.0.0)** - AI image generation library
  - Core functionality for image creation
  - Requires async/await pattern
  
- **Pillow (10.4.0)** - Image processing library
  - Required by Perchance for image manipulation
  
- **Playwright (1.48.0)** - Browser automation
  - Required by Perchance for certain generation features
  
- **Requests** - HTTP client library (API service only)
  - Used for service-to-service communication

### Environment Configuration
- **PERCHANCE_WORKER_URL** - Required environment variable pointing to deployed Render worker
  - Format: `https://your-worker.onrender.com`
  - Used by API to locate and communicate with worker service

### Deployment Architecture
- **Replit** - Main API hosting
  - Lightweight Flask app
  - Environment variable configuration
  
- **Render** - Worker hosting
  - Docker-based deployment
  - GitHub integration for continuous deployment
  - Separate repository recommended for worker code