from flask import Flask, request, jsonify
import asyncio
import perchance
from io import BytesIO
import traceback
import os
import base64

app = Flask(__name__)

def run_async(coro):
    """Helper function to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def image_to_base64(image_binary):
    """Convert image binary to base64 string"""
    if hasattr(image_binary, 'read'):
        if hasattr(image_binary, 'seek'):
            image_binary.seek(0)
        image_data = image_binary.read()
    else:
        image_data = image_binary
    
    return base64.b64encode(image_data).decode('utf-8')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Perchance Worker',
        'version': '3.0.0'
    }), 200

@app.route('/generate', methods=['POST'])
def generate_image():
    """
    Generate an image using Perchance and return as base64
    
    JSON Body:
    {
        "prompt": "text description",
        "seed": -1,  // optional
        "guidance_scale": 7.0,  // optional
        "shape": "square",  // optional: portrait, landscape, square
        "negative_prompt": ""  // optional
    }
    
    Returns:
    {
        "image_base64": "base64_encoded_image_data",
        "prompt": "...",
        "seed": 123,
        "shape": "square",
        "guidance_scale": 7.0
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'Missing required field: prompt'
            }), 400
        
        prompt = data['prompt']
        seed = data.get('seed', -1)
        guidance_scale = data.get('guidance_scale', 7.0)
        shape = data.get('shape', 'square')
        negative_prompt = data.get('negative_prompt')
        
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
            
            kwargs = {
                'seed': seed,
                'guidance_scale': guidance_scale,
                'shape': shape,
            }
            
            if negative_prompt:
                kwargs['negative_prompt'] = negative_prompt
            
            async with await gen.image(prompt, **kwargs) as result:
                binary = await result.download()
                return binary
        
        # Run async generation
        image_binary = run_async(generate())
        
        # Convert to base64
        image_base64 = image_to_base64(image_binary)
        
        # Return JSON response with base64 image
        response_data = {
            'image_base64': image_base64,
            'prompt': prompt,
            'seed': seed,
            'shape': shape,
            'guidance_scale': guidance_scale
        }
        
        if negative_prompt:
            response_data['negative_prompt'] = negative_prompt
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': 'Failed to generate image',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
