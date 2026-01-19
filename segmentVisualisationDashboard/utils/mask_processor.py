"""
Mask Processor Utility
Process masks and create overlays with RGB colors (Red, Green, Blue)
"""

import numpy as np
from PIL import Image
import cv2
from pathlib import Path


class MaskProcessor:
    """Process masks and create visualizations"""
    
    def __init__(self):
        # RGB colors for different classes (100% opacity)
        self.colors = [
            [255, 0, 0],    # Red
            [0, 255, 0],    # Green
            [0, 0, 255],    # Blue
            [255, 255, 0],  # Yellow
            [255, 0, 255],  # Magenta
            [0, 255, 255],  # Cyan
            [255, 128, 0],  # Orange
            [128, 0, 255],  # Purple
            [0, 128, 255],  # Light Blue
            [255, 192, 203], # Pink
        ]
    
    def get_color_for_class(self, class_id, class_colors_map=None):
        """Get RGB color for a class ID"""
        if class_colors_map and class_id in class_colors_map:
            return class_colors_map[class_id]
        
        # Use modulo to cycle through colors
        color_idx = int(class_id) % len(self.colors)
        return self.colors[color_idx]
    
    def create_mask_overlay(self, image, label_data, class_colors_map=None, opacity=1.0):
        """
        Create mask overlay on image
        
        Args:
            image: PIL Image or numpy array
            label_data: Label data from label_loader
            class_colors_map: Optional dict mapping class_id to RGB color
            opacity: Float between 0.0 and 1.0 for overlay opacity (1.0 = 100%, 0.0 = 0%)
        
        Returns:
            overlay_image: PIL Image with mask overlay
            mask_only_image: PIL Image showing only masks
        """
        # Convert image to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image.copy()
        
        # Handle grayscale images
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]
        
        h, w = img_array.shape[:2]
        
        # Create overlay and mask-only images
        overlay = img_array.copy()
        mask_only = np.zeros((h, w, 3), dtype=np.uint8)
        
        label_format = label_data.get('format', 'mask')
        
        if label_format == 'mask':
            # Pixel-level mask - lazy load on-demand
            mask_path = Path(label_data['mask_path'])
            
            # Load mask array only when needed for visualization
            mask_img = Image.open(mask_path)
            mask_array = np.array(mask_img)
            
            # Detect classes from mask if not already detected
            classes = label_data.get('classes', [])
            if not classes:
                # Detect classes on-demand
                unique_classes = np.unique(mask_array)
                classes = unique_classes[unique_classes > 0].tolist()
                # Update label_data for future use
                label_data['classes'] = classes
            
            # Ensure mask_array matches image dimensions
            if mask_array.shape[:2] != (h, w):
                mask_array = cv2.resize(mask_array, (w, h), interpolation=cv2.INTER_NEAREST)
            
            for class_id in classes:
                color = self.get_color_for_class(class_id, class_colors_map)
                mask = (mask_array == class_id).astype(np.float32)
                
                # Apply color overlay with opacity blending
                for c in range(3):
                    # Blend overlay color with original image based on opacity
                    # Formula: result = original * (1 - opacity * mask) + overlay_color * opacity * mask
                    overlay[:, :, c] = (overlay[:, :, c].astype(np.float32) * (1.0 - opacity * mask) + 
                                       color[c] * opacity * mask).astype(np.uint8)
                    # Mask-only image always shows full color (100% opacity)
                    mask_only[:, :, c] = np.where(mask > 0, color[c], mask_only[:, :, c]).astype(np.uint8)
        
        elif label_format in ['yolo', 'voc', 'json']:
            # Polygon-based masks
            masks = label_data.get('masks', [])
            
            for mask_info in masks:
                class_id = mask_info.get('class_id', 0)
                color = self.get_color_for_class(class_id, class_colors_map)
                
                if mask_info.get('type') == 'polygon':
                    polygon = mask_info.get('polygon', [])
                    if len(polygon) >= 6:  # At least 3 points
                        # Convert to numpy array of points
                        points = np.array(polygon, dtype=np.int32).reshape(-1, 2)
                        
                        # For YOLO format, convert normalized coordinates to pixel coordinates
                        if label_format == 'yolo':
                            # YOLO format uses normalized coordinates (0-1)
                            # Convert to pixel coordinates
                            points[:, 0] = (points[:, 0] * w).astype(np.int32)
                            points[:, 1] = (points[:, 1] * h).astype(np.int32)
                        
                        # Clip points to image boundaries
                        points[:, 0] = np.clip(points[:, 0], 0, w - 1)
                        points[:, 1] = np.clip(points[:, 1], 0, h - 1)
                        
                        # Create mask from polygon
                        mask = np.zeros((h, w), dtype=np.uint8)
                        cv2.fillPoly(mask, [points], 255)
                        
                        # Apply overlay (100% opacity)
                        for c in range(3):
                            overlay[:, :, c] = np.where(mask > 0, color[c], overlay[:, :, c])
                            mask_only[:, :, c] = np.where(mask > 0, color[c], mask_only[:, :, c])
                
                elif mask_info.get('type') == 'bbox':
                    bbox = mask_info.get('bbox', [])
                    if len(bbox) == 4:
                        xmin, ymin, xmax, ymax = bbox
                        # Clip to image boundaries
                        xmin = max(0, min(xmin, w - 1))
                        ymin = max(0, min(ymin, h - 1))
                        xmax = max(0, min(xmax, w - 1))
                        ymax = max(0, min(ymax, h - 1))
                        # Draw rectangle
                        overlay[ymin:ymax, xmin:xmax] = color
                        mask_only[ymin:ymax, xmin:xmax] = color
        
        return Image.fromarray(overlay), Image.fromarray(mask_only)
    
    def create_class_legend(self, classes, class_colors_map=None, class_names_map=None):
        """
        Create legend mapping classes to colors
        
        Returns:
            dict: {class_id: {'color': [R, G, B], 'name': str}}
        """
        legend = {}
        
        for class_id in classes:
            color = self.get_color_for_class(class_id, class_colors_map)
            name = class_names_map.get(class_id, f"Class {class_id}") if class_names_map else f"Class {class_id}"
            
            legend[class_id] = {
                'color': color,
                'name': name,
                'hex': f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            }
        
        return legend

