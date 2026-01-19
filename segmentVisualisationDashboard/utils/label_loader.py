"""
Label Loader Utility
Supports multiple label formats: YOLO, Pascal VOC, Mask PNG, Custom JSON
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image
import cv2


class LabelLoader:
    """Load labels from various formats"""
    
    def __init__(self, images_path, labels_path, label_format):
        self.images_path = Path(images_path)
        self.labels_path = Path(labels_path)
        self.label_format = label_format
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
    def load_all(self):
        """Load all images and their corresponding labels"""
        # Starting data loading
        data = []
        
        # Get all image files recursively (including subdirectories)
        image_files = []
        for ext in self.image_extensions:
            # Search recursively in subdirectories
            image_files.extend(list(self.images_path.rglob(f'*{ext}')))
            image_files.extend(list(self.images_path.rglob(f'*{ext.upper()}')))
        
        # Remove duplicates and sort
        image_files = sorted(list(set(image_files)))
        # Found image files
        
        # For mask format, build a lookup dictionary for faster matching
        mask_lookup = {}
        mask_classes_cache = {}  # Cache classes for each mask
        if self.label_format == 'mask':
            # Building mask file lookup and detecting classes
            # Get all mask files once
            mask_files = []
            for ext in ['.png', '.PNG']:
                mask_files.extend(list(self.labels_path.rglob(f'*{ext}')))
            
            # Build lookup: image_name -> mask_path and detect classes efficiently
            processed = 0
            for mask_file in mask_files:
                mask_stem = mask_file.stem
                # Remove common suffixes
                for suffix in ['_mask', '_label']:
                    if mask_stem.endswith(suffix):
                        mask_stem = mask_stem[:-len(suffix)]
                        break
                mask_lookup[mask_stem] = mask_file
                
                # Efficiently detect classes by downsampling the entire image
                try:
                    with Image.open(mask_file) as img:
                        width, height = img.size
                        
                        # Downsample to max 200x200 for class detection (fast but thorough)
                        max_size = 200
                        if width > max_size or height > max_size:
                            # Calculate scale to fit within max_size
                            scale = min(max_size / width, max_size / height)
                            new_width = int(width * scale)
                            new_height = int(height * scale)
                            # Resize using nearest neighbor to preserve class IDs
                            img_resized = img.resize((new_width, new_height), Image.NEAREST)
                            mask_array = np.array(img_resized)
                            del img_resized
                        else:
                            # Small enough, load directly
                            mask_array = np.array(img)
                        
                        # Get unique classes from downsampled image
                        unique_classes = np.unique(mask_array)
                        unique_classes = unique_classes[unique_classes > 0].tolist()
                        
                        mask_classes_cache[mask_stem] = unique_classes
                        
                        # Free memory immediately
                        del mask_array
                except Exception as e:
                    # If detection fails, set empty classes (will be detected on-demand)
                    mask_classes_cache[mask_stem] = []
                
                processed += 1
                # Progress update (every 500 files)
            
            # Built lookup for mask files with class detection
        
        # Process images
        processed = 0
        for img_path in image_files:
            img_name = img_path.stem
            label_data = self._load_label(img_name, img_path, mask_lookup, mask_classes_cache)
            
            if label_data is not None:
                data.append({
                    'image_path': str(img_path),
                    'image_name': img_path.name,
                    'label_data': label_data
                })
            
            processed += 1
        
        # Completed loading images with labels
        return data
    
    def _load_label(self, image_name, image_path=None, mask_lookup=None, mask_classes_cache=None):
        """Load label for a specific image based on format"""
        if self.label_format == 'yolo':
            return self._load_yolo(image_name)
        elif self.label_format == 'voc':
            return self._load_voc(image_name)
        elif self.label_format == 'mask':
            return self._load_mask(image_name, image_path, mask_lookup, mask_classes_cache)
        elif self.label_format == 'json':
            return self._load_json(image_name)
        else:
            raise ValueError(f"Unsupported label format: {self.label_format}")
    
    def _load_yolo(self, image_name):
        """Load YOLO format label (.txt file)"""
        label_path = self.labels_path / f"{image_name}.txt"
        
        if not label_path.exists():
            return None
        
        masks = []
        classes = []
        
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                class_id = int(parts[0])
                # YOLO format: class_id x1 y1 x2 y2 x3 y3 ... (normalized coordinates)
                # For segmentation, we need polygon points
                coords = [float(x) for x in parts[1:]]
                
                # Convert normalized coordinates to pixel coordinates
                # Note: We'll need image dimensions for this, but for now store normalized
                masks.append({
                    'class_id': class_id,
                    'polygon': coords,
                    'type': 'polygon'
                })
                classes.append(class_id)
        
        return {
            'format': 'yolo',
            'masks': masks,
            'classes': list(set(classes))
        }
    
    def _load_voc(self, image_name):
        """Load Pascal VOC format label (.xml file)"""
        label_path = self.labels_path / f"{image_name}.xml"
        
        if not label_path.exists():
            return None
        
        try:
            tree = ET.parse(label_path)
            root = tree.getroot()
            
            masks = []
            classes = []
            
            for obj in root.findall('object'):
                class_name = obj.find('name').text
                class_id = hash(class_name) % 1000  # Simple hash for class ID
                
                # Get polygon or bounding box
                polygon = obj.find('polygon')
                if polygon is not None:
                    points = []
                    for pt in polygon.findall('pt'):
                        x = int(pt.find('x').text)
                        y = int(pt.find('y').text)
                        points.extend([x, y])
                    
                    masks.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'polygon': points,
                        'type': 'polygon'
                    })
                else:
                    # Fallback to bounding box
                    bbox = obj.find('bndbox')
                    if bbox is not None:
                        xmin = int(bbox.find('xmin').text)
                        ymin = int(bbox.find('ymin').text)
                        xmax = int(bbox.find('xmax').text)
                        ymax = int(bbox.find('ymax').text)
                        
                        masks.append({
                            'class_id': class_id,
                            'class_name': class_name,
                            'bbox': [xmin, ymin, xmax, ymax],
                            'type': 'bbox'
                        })
                
                classes.append(class_id)
            
            return {
                'format': 'voc',
                'masks': masks,
                'classes': list(set(classes))
            }
        except Exception as e:
            print(f"Error loading VOC file {label_path}: {e}")
            return None
    
    def _load_mask(self, image_name, image_path=None, mask_lookup=None, mask_classes_cache=None):
        """Load mask PNG file (pixel-level masks) - lazy loading (only stores path, not array)"""
        mask_path = None
        
        # Use lookup dictionary if available (much faster)
        if mask_lookup is not None:
            mask_path = mask_lookup.get(image_name)
        else:
            # Fallback: search recursively (slower)
            mask_patterns = [
                f"{image_name}.png",
                f"{image_name}_mask.png",
                f"{image_name}_label.png",
            ]
            
            # First try direct match in root
            for pattern in mask_patterns:
                potential_path = self.labels_path / pattern
                if potential_path.exists():
                    mask_path = potential_path
                    break
            
            # If not found, search recursively in subdirectories
            if mask_path is None:
                for pattern in mask_patterns:
                    matches = list(self.labels_path.rglob(pattern))
                    if matches:
                        mask_path = matches[0]
                        break
        
        if mask_path is None or not mask_path.exists():
            return None
        
        try:
            # OPTIMIZATION: Don't load mask images into memory at all during initial load!
            # Just store the path - load everything on-demand when visualizing
            # This makes loading instant and uses zero memory for masks
            
            # Get class name from subdirectory if available
            class_name = None
            if mask_path.parent != self.labels_path:
                class_name = mask_path.parent.name
            
            # Get image dimensions without loading the array (just metadata)
            # This is very fast - just reads image header
            try:
                with Image.open(mask_path) as img:
                    width, height = img.size
            except:
                # Fallback: use default if we can't read dimensions
                width, height = 0, 0
            
            # Get classes from cache if available (detected during lookup building)
            classes = []
            if mask_classes_cache is not None:
                classes = mask_classes_cache.get(image_name, [])
            
            # Return metadata - mask array will be loaded on-demand
            return {
                'format': 'mask',
                'mask_path': str(mask_path),
                'classes': classes,  # Classes detected during lookup building
                'shape': (height, width),  # Store shape for reference
                'class_name': class_name,
                'lazy_load': True  # Flag to indicate lazy loading
            }
        except Exception as e:
            print(f"Error loading mask file {mask_path}: {e}")
            return None
    
    def _load_json(self, image_name):
        """Load custom JSON format label"""
        # Try common JSON naming patterns
        json_patterns = [
            f"{image_name}.json",
            f"{image_name}_label.json",
            f"{image_name}_annotation.json"
        ]
        
        json_path = None
        for pattern in json_patterns:
            potential_path = self.labels_path / pattern
            if potential_path.exists():
                json_path = potential_path
                break
        
        if json_path is None:
            return None
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Extract classes and masks from JSON
            # Expected format: {"classes": [...], "masks": [...]}
            classes = []
            masks = []
            
            if isinstance(data, dict):
                if 'masks' in data:
                    masks = data['masks']
                    if masks:
                        if isinstance(masks[0], dict) and 'class_id' in masks[0]:
                            classes = [m.get('class_id') for m in masks]
                        elif isinstance(masks[0], dict) and 'class' in masks[0]:
                            classes = [m.get('class') for m in masks]
                
                if 'classes' in data:
                    classes = data['classes']
            
            return {
                'format': 'json',
                'masks': masks,
                'classes': list(set(classes)) if classes else [],
                'raw_data': data
            }
        except Exception as e:
            print(f"Error loading JSON file {json_path}: {e}")
            return None

