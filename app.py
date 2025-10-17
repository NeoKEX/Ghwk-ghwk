from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get worker URL from environment variable
WORKER_URL = os.environ.get('PERCHANCE_WORKER_URL', '')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Image Generation API',
        'version': '2.0.0',
        'worker_configured': bool(WORKER_URL)
    }), 200

@app.route('/generate', methods=['GET'])
def generate_image():
    """
    Generate an image using Perchance API via Render worker
    
    Query Parameters:
    - prompt (required): Text description of the image
    - seed (optional): Random seed for reproducibility (-1 for random)
    - guidance_scale (optional): How closely to follow the prompt (default: 7.0)
    - shape (optional): Image shape - 'portrait', 'landscape', or 'square' (default: 'square')
    - negative_prompt (optional): What to avoid in the image
    
    Returns:
    {
        "success": true,
        "image_url": "https://i.imgur.com/xxxxx.png",
        "prompt": "...",
        "seed": 123,
        "shape": "square",
        "guidance_scale": 7.0
    }
    """
    try:
        # Check if worker is configured
        if not WORKER_URL:
            return jsonify({
                'success': False,
                'error': 'Worker service not configured',
                'details': 'Please set PERCHANCE_WORKER_URL environment variable with your Render worker URL'
            }), 503
        
        # Get and validate parameters
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: prompt'
            }), 400
        
        # Optional parameters
        seed = request.args.get('seed', default=-1, type=int)
        guidance_scale = request.args.get('guidance_scale', default=7.0, type=float)
        shape = request.args.get('shape', default='square', type=str)
        negative_prompt = request.args.get('negative_prompt', type=str)
        
        # Validate shape
        valid_shapes = ['portrait', 'landscape', 'square']
        if shape not in valid_shapes:
            return jsonify({
                'success': False,
                'error': f'Invalid shape. Must be one of: {", ".join(valid_shapes)}'
            }), 400
        
        # Validate guidance_scale
        if guidance_scale < 0 or guidance_scale > 20:
            return jsonify({
                'success': False,
                'error': 'Guidance scale must be between 0 and 20'
            }), 400
        
        # Prepare request to worker
        worker_data = {
            'prompt': prompt,
            'seed': seed,
            'guidance_scale': guidance_scale,
            'shape': shape,
        }
        
        if negative_prompt:
            worker_data['negative_prompt'] = negative_prompt
        
        # Call worker service
        worker_response = requests.post(
            f'{WORKER_URL}/generate',
            json=worker_data,
            timeout=120  # 2 minute timeout for image generation
        )
        
        # Check if worker request was successful
        if worker_response.status_code != 200:
            try:
                error_data = worker_response.json()
                return jsonify({
                    'success': False,
                    'error': 'Worker service error',
                    'details': error_data.get('error', 'Unknown error')
                }), worker_response.status_code
            except:
                return jsonify({
                    'success': False,
                    'error': 'Worker service error',
                    'details': f'HTTP {worker_response.status_code}'
                }), worker_response.status_code
        
        # Get JSON response from worker
        result = worker_response.json()
        
        # Return success response with image URL
        return jsonify({
            'success': True,
            'image_url': result.get('image_url'),
            'prompt': result.get('prompt'),
            'seed': result.get('seed'),
            'shape': result.get('shape'),
            'guidance_scale': result.get('guidance_scale'),
            'negative_prompt': result.get('negative_prompt')
        }), 200
    
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Worker service timeout',
            'details': 'Image generation took too long. Please try again.'
        }), 504
    
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Cannot connect to worker service',
            'details': 'Please check PERCHANCE_WORKER_URL or ensure the worker service is running'
        }), 503
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate image',
            'details': str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    return jsonify({
        'name': 'Image Generation API',
        'version': '2.0.0',
        'worker_configured': bool(WORKER_URL),
        'worker_url': WORKER_URL if WORKER_URL else 'Not configured',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/generate': {
                'method': 'GET',
                'description': 'Generate an image from a text prompt using Perchance and get the image URL',
                'parameters': {
                    'prompt': {
                        'type': 'string',
                        'required': True,
                        'description': 'Text description of the image to generate'
                    },
                    'seed': {
                        'type': 'integer',
                        'required': False,
                        'default': -1,
                        'description': 'Random seed for reproducibility (-1 for random)'
                    },
                    'guidance_scale': {
                        'type': 'float',
                        'required': False,
                        'default': 7.0,
                        'description': 'How closely to follow the prompt (0-20)'
                    },
                    'shape': {
                        'type': 'string',
                        'required': False,
                        'default': 'square',
                        'description': "Image shape: 'portrait', 'landscape', or 'square'"
                    },
                    'negative_prompt': {
                        'type': 'string',
                        'required': False,
                        'description': 'What to avoid in the image (e.g., "blurry, low quality")'
                    }
                },
                'example': '/generate?prompt=sunset over mountains&guidance_scale=7.5&shape=landscape&negative_prompt=blurry',
                'response': {
                    'success': True,
                    'image_url': 'https://i.imgur.com/xxxxx.png',
                    'prompt': '...',
                    'seed': 123,
                    'shape': 'square',
                    'guidance_scale': 7.0
                }
            }
        },
        'setup_instructions': {
            '1': 'Create an Imgur account and get a Client ID from https://api.imgur.com/oauth2/addclient',
            '2': 'Deploy the worker service to Render using files in render_worker/ folder',
            '3': 'Set IMGUR_CLIENT_ID environment variable in Render worker settings',
            '4': 'Get your Render worker URL (e.g., https://your-worker.onrender.com)',
            '5': 'Deploy the API service to Render',
            '6': 'Set PERCHANCE_WORKER_URL environment variable in Render API settings',
            '7': 'Test the API!'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
