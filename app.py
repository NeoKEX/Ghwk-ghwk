from flask import Flask, request, send_file, jsonify
import asyncio
import perchance
from io import BytesIO
import traceback
import os

os.environ['PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS'] = 'true'

app = Flask(__name__)

def run_async(coro):
    """Helper function to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Image Generation API',
        'version': '1.0.0'
    }), 200

@app.route('/generate', methods=['GET'])
def generate_image():
    """
    Generate an image using Perchance API
    
    Query Parameters:
    - prompt (required): Text description of the image
    - seed (optional): Random seed for reproducibility (-1 for random)
    - guidance_scale (optional): How closely to follow the prompt (default: 7.0)
    - shape (optional): Image shape - 'portrait', 'landscape', or 'square' (default: 'square')
    - negative_prompt (optional): What to avoid in the image
    """
    try:
        # Get and validate parameters
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'error': 'Missing required parameter: prompt'
            }), 400
        
        # Add casual photo style to the prompt
        styled_prompt = f"casual photo, {prompt}"
        
        # Optional parameters
        seed = request.args.get('seed', default=-1, type=int)
        guidance_scale = request.args.get('guidance_scale', default=7.0, type=float)
        shape = request.args.get('shape', default='square', type=str)
        negative_prompt = request.args.get('negative_prompt', type=str)
        
        # Validate shape
        valid_shapes = ['portrait', 'landscape', 'square']
        if shape not in valid_shapes:
            return jsonify({
                'error': f'Invalid shape. Must be one of: {", ".join(valid_shapes)}'
            }), 400
        
        # Validate guidance_scale
        if guidance_scale < 0 or guidance_scale > 20:
            return jsonify({
                'error': 'Guidance scale must be between 0 and 20'
            }), 400
        
        # Generate image using perchance
        async def generate():
            gen = perchance.ImageGenerator()
            
            # Create kwargs for the image generation
            kwargs = {
                'seed': seed,
                'guidance_scale': guidance_scale,
                'shape': shape,
            }
            
            if negative_prompt:
                kwargs['negative_prompt'] = negative_prompt
            
            async with await gen.image(styled_prompt, **kwargs) as result:
                binary = await result.download()
                return binary
        
        # Run async generation
        image_binary = run_async(generate())
        
        # Return the image
        return send_file(
            image_binary,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'generated_{prompt[:30]}.png'
        )
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error generating image: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': 'Failed to generate image',
            'details': str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    return jsonify({
        'name': 'Image Generation API',
        'version': '1.0.0',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/generate': {
                'method': 'GET',
                'description': 'Generate an image from a text prompt (casual photo style)',
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
                'example': '/generate?prompt=sunset over mountains&guidance_scale=7.5&shape=landscape&negative_prompt=blurry'
            }
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
