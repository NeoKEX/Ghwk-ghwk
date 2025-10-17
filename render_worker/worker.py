from flask import Flask, request, send_file, jsonify
import asyncio
import perchance
from io import BytesIO
import traceback
import os

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
        'service': 'Perchance Worker',
        'version': '1.0.0'
    }), 200

@app.route('/generate', methods=['POST'])
def generate_image():
    """
    Generate an image using Perchance
    
    JSON Body:
    {
        "prompt": "text description",
        "seed": -1,  // optional
        "guidance_scale": 7.0,  // optional
        "shape": "square",  // optional: portrait, landscape, square
        "negative_prompt": ""  // optional
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
        
        # Return the image - handle file-like objects or raw bytes
        if hasattr(image_binary, 'read'):
            # It's a file-like object (BytesIO, AsyncBufferedIOBase, etc.)
            if hasattr(image_binary, 'seek'):
                image_binary.seek(0)  # Reset pointer to start if possible
            return send_file(
                image_binary,
                mimetype='image/png',
                as_attachment=False,
                download_name='generated.png'
            )
        else:
            # It's raw bytes, wrap in BytesIO
            return send_file(
                BytesIO(image_binary),
                mimetype='image/png',
                as_attachment=False,
                download_name='generated.png'
            )
    
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
