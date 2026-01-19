# Segmentation Visualization Dashboard

A web-based dashboard for visualizing and analyzing annotated segmentation data with support for multiple annotation formats.

## Features

- **Multiple Format Support**: YOLO, Pascal VOC, Mask PNG, and Custom JSON
- **Interactive Visualization**: View original images, masks, and overlays side-by-side
- **Adjustable Overlay Opacity**: Control mask transparency in real-time
- **Efficient Performance**: Optimized for large datasets (2000+ images)
- **Modal View**: Expand images for detailed inspection with zoom/pan
- **Statistics Dashboard**: View dataset statistics and class distributions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Configure paths**:
   - Navigate to the **Settings** tab
   - Select your images folder and labels folder
   - Choose the annotation format (YOLO, Pascal VOC, Mask PNG, or Custom JSON)
   - Click "Load Data"

3. **View data**:
   - **Statistics** tab: View dataset statistics and class distribution
   - **Image Viewer** tab: Browse images with pagination (5 per page)

## Supported Formats

- **YOLO**: `.txt` files with normalized bounding box coordinates
- **Pascal VOC**: `.xml` files with object annotations
- **Mask PNG**: Pixel-level mask images (PNG format)
- **Custom JSON**: Custom annotation format

## Image Viewer Features

- **Card-based Layout**: Each image displays Original, Mask, and Overlay views
- **Click to Expand**: Click any image to view in full-screen modal
- **Overlay Control**: Adjust opacity slider in modal header when viewing overlays
- **Pagination**: Navigate through large datasets efficiently (5 images per page)

## Requirements

- Python 3.8+
- Dash
- Dash Bootstrap Components
- Pillow
- NumPy
- OpenCV

## Project Structure

```
segmentVisualisationDashboard/
├── app.py                 # Main application
├── components/            # UI components
│   ├── settings.py       # Settings tab
│   ├── statistics.py     # Statistics tab
│   └── image_viewer.py   # Image viewer tab
├── utils/                # Utility functions
│   ├── label_loader.py   # Label format loaders
│   ├── mask_processor.py # Mask processing
│   └── image_utils.py    # Image utilities
└── assets/               # CSS and static assets
```
