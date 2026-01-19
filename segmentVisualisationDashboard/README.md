# Segmentation Data Visualization Dashboard

A utility dashboard for visualizing annotated segmentation data with masks and overlays. Built with Dash framework, similar to the analysisDashboard architecture.

## Features

### ✅ Core Features

1. **⚙️ Settings Tab**
   - Configure images folder path
   - Configure labels folder path
   - Select label format (YOLO, Pascal VOC, Mask PNG, Custom JSON)
   - Load and process all images with labels
   - Reset data functionality

2. **📊 Statistics Tab**
   - Total images count
   - Total annotations count
   - Unique classes count
   - Images with/without labels
   - Class distribution chart
   - Average annotations per image

3. **🖼️ Image Viewer Tab**
   - **Three View Modes**:
     - Original: Show original image only
     - Overlay: Show image with mask overlay (100% opacity RGB colors)
     - Mask Only: Show only the mask visualization
   - **Zoom and Pan**: Interactive Plotly-based image viewer with zoom/pan capabilities
   - **Navigation**: First, Previous, Next, Last buttons
   - **Search**: Search images by filename
   - **Class Legend**: Color-coded legend showing all classes
   - **Image Information**: Display image dimensions, file size, and class information

## Supported Label Formats

1. **YOLO Format (.txt)**
   - Text files with normalized polygon coordinates
   - Format: `class_id x1 y1 x2 y2 x3 y3 ...`
   - One file per image

2. **Pascal VOC XML (.xml)**
   - XML files with polygon or bounding box annotations
   - Standard Pascal VOC format
   - One file per image

3. **Mask PNG Files (.png)**
   - Pixel-level masks with class IDs
   - Each pixel value represents a class ID
   - Background is typically 0
   - Supports common naming patterns: `{image_name}.png`, `{image_name}_mask.png`, `{image_name}_label.png`

4. **Custom JSON (.json)**
   - Custom JSON format with masks and classes
   - Flexible structure
   - Supports: `{image_name}.json`, `{image_name}_label.json`, `{image_name}_annotation.json`

## Installation

```bash
cd /Users/saurabhsingh/Downloads/root/segmentVisualisationDashboard
pip install -r requirements.txt
```

## Usage

### Starting the Dashboard

```bash
python app.py
```

The dashboard will be available at: `http://localhost:8051`

### Workflow

1. **Configure Settings**:
   - Navigate to the **⚙️ Settings** tab
   - Enter the path to your images folder
   - Enter the path to your labels folder
   - Select the label format matching your annotation files
   - Click **"🔄 Load Data"** to load and process all images

2. **View Statistics**:
   - Navigate to the **📊 Statistics** tab
   - Review dataset statistics and class distribution

3. **Visualize Images**:
   - Navigate to the **🖼️ Image Viewer** tab
   - Use navigation buttons to browse through images
   - Toggle between Original, Overlay, and Mask Only views
   - Use zoom/pan controls in the Plotly viewer
   - Search for specific images by name

## Color Scheme

The dashboard uses RGB colors (100% opacity) for mask visualization:
- Red (255, 0, 0)
- Green (0, 255, 0)
- Blue (0, 0, 255)
- Yellow (255, 255, 0)
- Magenta (255, 0, 255)
- Cyan (0, 255, 255)
- Orange (255, 128, 0)
- Purple (128, 0, 255)
- Light Blue (0, 128, 255)
- Pink (255, 192, 203)

Colors are assigned to classes in order and cycle if there are more than 10 classes.

## File Structure

```
segmentVisualisationDashboard/
├── app.py                    # Main Dash application
├── components/               # Tab components
│   ├── __init__.py
│   ├── settings.py          # Settings tab
│   ├── statistics.py        # Statistics tab
│   └── image_viewer.py      # Image Viewer tab
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── label_loader.py       # Load different label formats
│   ├── mask_processor.py    # Process masks and overlays
│   └── image_utils.py       # Image utilities
├── assets/                   # Static assets (CSS)
│   └── custom.css
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Dependencies

See `requirements.txt` for full list. Main dependencies:
- `dash` - Web framework
- `dash-bootstrap-components` - UI components
- `pandas` - Data manipulation
- `plotly` - Interactive visualizations with zoom/pan
- `numpy` - Numerical operations
- `Pillow` - Image processing
- `opencv-python` - Image and mask processing

## Performance Considerations

- Designed to handle ~2000+ images efficiently
- Images are loaded on-demand when navigating
- Mask processing is optimized for pixel-level masks
- Large images are automatically resized for display (max 2048px)

## Notes

- **Mask Overlay**: Uses 100% opacity RGB colors as specified
- **Zoom/Pan**: Implemented using Plotly's interactive features
- **Label Matching**: Images and labels are matched by filename (without extension)
- **Format Detection**: Automatically detects label files based on selected format
- **Error Handling**: Gracefully handles missing labels or corrupted files

## Troubleshooting

### Common Issues:

1. **"No matching images and labels found"**:
   - Verify image and label folder paths are correct
   - Ensure label format matches your files
   - Check that image and label filenames match (excluding extensions)

2. **Images not displaying**:
   - Check that image files are readable
   - Verify image formats are supported (.jpg, .png, .bmp, .tiff)
   - Check console for error messages

3. **Masks not showing**:
   - Verify label format is correct
   - For mask PNG format, ensure pixel values represent class IDs
   - Check that mask dimensions match image dimensions (or close)

4. **Zoom/Pan not working**:
   - Ensure Plotly is properly installed
   - Check browser console for JavaScript errors
   - Try refreshing the page

## Support

For issues or questions, refer to the code comments in each component file or check the implementation details in:
- `components/settings.py` - Data loading logic
- `components/image_viewer.py` - Image viewing and visualization
- `components/statistics.py` - Statistics calculations
- `utils/label_loader.py` - Label format parsing
- `utils/mask_processor.py` - Mask overlay generation

