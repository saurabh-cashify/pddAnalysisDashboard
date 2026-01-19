"""
Image Utilities
Helper functions for image processing and display
"""

import base64
from io import BytesIO
from PIL import Image
import numpy as np


def pil_to_base64(image):
    """Convert PIL Image to base64 string for display in Dash"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def get_image_info(image_path):
    """Get image dimensions and file size"""
    try:
        from pathlib import Path
        # Convert to Path if it's a string
        if isinstance(image_path, str):
            image_path = Path(image_path)
        
        img = Image.open(image_path)
        width, height = img.size
        file_size = image_path.stat().st_size / 1024  # KB
        
        return {
            'width': width,
            'height': height,
            'size_kb': round(file_size, 2),
            'mode': img.mode
        }
    except Exception as e:
        print(f"Error getting image info for {image_path}: {e}")
        return None


def resize_image_if_needed(image, max_size=2048):
    """Resize image if it's too large, maintaining aspect ratio"""
    if isinstance(image, Image.Image):
        width, height = image.size
    else:
        height, width = image.shape[:2]
        image = Image.fromarray(image)
    
    if width <= max_size and height <= max_size:
        return image
    
    # Calculate new dimensions
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

