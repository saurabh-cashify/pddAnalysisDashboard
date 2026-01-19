"""
Image Viewer Tab Component
Display images with mask overlays in card-based layout similar to analysisDashboard
"""

from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
from pathlib import Path
import sys
from PIL import Image
import numpy as np
import base64
from io import BytesIO

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.mask_processor import MaskProcessor
from utils.image_utils import pil_to_base64, get_image_info


def create_image_viewer_tab():
    """Create the Image Viewer tab layout"""
    
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3("🖼️ Image Viewer", className="mb-4", style={"color": "#3b82f6"}),
                
                # Statistics bar (only pagination info)
                html.Div(id="viewer-stats", className="mb-4"),
                
            ])
        ], className="mb-4"),
        
        # Record Display Area (cards with images)
        html.Div(id="record-display", children=[
            html.Div([
                html.Div(className="spinner"),
                html.P("Load data in Settings tab to view images...", className="text-center mt-3", style={"color": "#3b82f6"})
            ], className="text-center py-5")
        ]),
        
        # Navigation Controls (for pages of 10 records)
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("⏮️ First Page", id="first-page-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("◀️ Prev", id="prev-page-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-start"),
                    dbc.Col([
                        html.Div([
                            html.Span("Records ", style={"fontSize": "0.9em"}),
                            html.Span(id="page-start", children="1", style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span("-", style={"margin": "0 4px"}),
                            html.Span(id="page-end", children="5", style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span(" of ", style={"margin": "0 8px"}),
                            html.Span(id="total-records", children="0", style={"fontSize": "1.2em", "fontWeight": "600"}),
                        ], className="text-center", style={"lineHeight": "38px"})
                    ], md=4),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Next ▶️", id="next-page-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("Last Page ⏭️", id="last-page-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-end"),
                ])
            ])
        ], className="mt-4"),
        
    ], fluid=True)


def create_record_card(record, record_index, class_colors, overlay_opacity=1.0):
    """Create a card for a single image record showing Original, Mask, and Overlay with expandable overlay section"""
    
    image_path = record['image_path']
    image_name = record['image_name']
    label_data = record.get('label_data')
    
    # Load images efficiently (only process what's needed)
    try:
        img = Image.open(image_path)
        
        # Resize large images for display efficiency (max 800px on longest side)
        max_display_size = 800
        width, height = img.size
        if width > max_display_size or height > max_display_size:
            scale = min(max_display_size / width, max_display_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        processor = MaskProcessor()
        
        # Create all three views
        original_img = img.copy()
        
        if label_data:
            overlay_img, mask_img = processor.create_mask_overlay(img, label_data, class_colors, opacity=overlay_opacity)
        else:
            # No label data - show placeholder
            overlay_img = img.copy()
            mask_img = Image.new('RGB', img.size, (0, 0, 0))
        
        # Convert to base64 for display
        original_b64 = pil_to_base64(original_img)
        mask_b64 = pil_to_base64(mask_img)
        overlay_b64 = pil_to_base64(overlay_img)
        
        # Create clickable images
        image_style = {
            "width": "100%",
            "maxHeight": "300px",
            "objectFit": "contain",
            "borderRadius": "8px",
            "border": "1px solid #e2e8f0",
            "cursor": "pointer"
        }
        
        original_img_elem = html.Img(
            src=original_b64,
            style=image_style,
            className="hover-shadow",
            id={"type": "image-clickable", "view": "original", "index": record_index},
            n_clicks=0
        )
        
        mask_img_elem = html.Img(
            src=mask_b64,
            style=image_style,
            className="hover-shadow",
            id={"type": "image-clickable", "view": "mask", "index": record_index},
            n_clicks=0
        )
        
        overlay_img_elem = html.Img(
            src=overlay_b64,
            style=image_style,
            className="hover-shadow",
            id={"type": "image-clickable", "view": "overlay", "index": record_index},
            n_clicks=0
        )
        
        # Get image info
        img_info = get_image_info(image_path)
        info_text = []
        if img_info:
            info_text.append(f"{img_info['width']} x {img_info['height']} px")
            info_text.append(f"{img_info['size_kb']} KB")
        
        if label_data:
            classes = label_data.get('classes', [])
            if classes:
                info_text.append(f"{len(classes)} class(es)")
        
        # Create card
        card = dbc.Card([
            dbc.CardHeader([
                html.H5(image_name, className="mb-0", style={"fontSize": "1em", "fontWeight": "600"})
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.P("Original", className="text-center mb-2", style={"fontWeight": "600", "color": "#3b82f6"}),
                            html.Div(original_img_elem, style={"textAlign": "center"})
                        ])
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.P("Mask", className="text-center mb-2", style={"fontWeight": "600", "color": "#3b82f6"}),
                            html.Div(mask_img_elem, style={"textAlign": "center"})
                        ])
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.P("Overlay", className="text-center mb-2", style={"fontWeight": "600", "color": "#3b82f6"}),
                            html.Div(overlay_img_elem, style={"textAlign": "center"})
                        ])
                    ], md=4),
                ]),
                html.Hr(),
                html.P([
                    html.Small(" | ".join(info_text), className="text-muted")
                ], className="mb-0 text-center")
            ])
        ], className="mb-3", style={"boxShadow": "0 2px 8px rgba(0,0,0,0.1)"})
        
        return card
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return dbc.Card([
            dbc.CardBody([
                html.P(f"Error loading {image_name}: {str(e)}", className="text-danger")
            ])
        ], className="mb-3")


def register_image_viewer_callbacks(app):
    """Register callbacks for image viewer tab"""
    
    @app.callback(
        [
            Output('viewer-stats', 'children'),
            Output('total-records', 'children'),
            Output('page-start', 'children'),
            Output('page-end', 'children'),
            Output('record-display', 'children'),
            Output('current-index-store', 'data'),
        ],
        [
            Input('data-store', 'data'),
            Input('main-tabs', 'active_tab'),  # Trigger when tab changes
            Input('current-index-store', 'data'),
            Input('first-page-btn', 'n_clicks'),
            Input('prev-page-btn', 'n_clicks'),
            Input('next-page-btn', 'n_clicks'),
            Input('last-page-btn', 'n_clicks'),
        ],
        [
            State('class-colors-store', 'data'),
            State('overlay-opacity-store', 'data'),
        ]
    )
    def update_record_display(data_store, active_tab, current_page, first_clicks, prev_clicks, next_clicks, last_clicks, class_colors, opacity_store):
        """Update record display with pagination"""
        
        # Debug logging removed for cleaner console output
        
        # Only process if we're on the viewer tab
        if active_tab != 'viewer':
            return (
                dbc.Alert("No data loaded. Please load data in Settings tab.", color="warning"),
                "0", "1", "0",
                html.Div([
                    html.Div(className="spinner"),
                    html.P("Load data in Settings tab to view images...", className="text-center mt-3", style={"color": "#3b82f6"})
                ], className="text-center py-5"),
                0
            )
        
        ctx = callback_context
        if not ctx.triggered:
            trigger_id = None
        else:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Get data
        if not data_store or 'data' not in data_store:
            return (
                dbc.Alert("No data loaded. Please load data in Settings tab.", color="warning"),
                "0", "1", "0",
                html.Div([
                    html.Div(className="spinner"),
                    html.P("Load data in Settings tab to view images...", className="text-center mt-3", style={"color": "#3b82f6"})
                ], className="text-center py-5"),
                0
            )
        
        data = data_store['data']
        total = len(data)
        
        if total == 0:
            return (
                dbc.Alert("No images found.", color="warning"),
                "0", "1", "0",
                html.Div("No images to display", className="text-center text-muted py-5"),
                0
            )
        
        # No search filtering - show all data
        filtered_data = data
        filtered_total = len(filtered_data)
        
        # Handle pagination (5 records per page for better performance)
        records_per_page = 5
        total_pages = max(1, (filtered_total + records_per_page - 1) // records_per_page)
        current_page = current_page or 0
        current_page = max(0, min(current_page, total_pages - 1))
        
        if trigger_id == 'first-page-btn':
            current_page = 0
        elif trigger_id == 'prev-page-btn':
            current_page = max(0, current_page - 1)
        elif trigger_id == 'next-page-btn':
            current_page = min(total_pages - 1, current_page + 1)
        elif trigger_id == 'last-page-btn':
            current_page = total_pages - 1
        
        # Get page records (only process 5 records at a time for efficiency)
        start_idx = current_page * records_per_page
        end_idx = min(start_idx + records_per_page, filtered_total)
        page_records = filtered_data[start_idx:end_idx]
        
        # Use opacity store (updated by separate callback)
        opacity_dict = opacity_store or {}
        
        # Create cards for each record with individual opacity values
        cards = []
        for idx, record in enumerate(page_records):
            global_idx = start_idx + idx
            # Get opacity for this specific record if available, otherwise default to 100%
            opacity_value = opacity_dict.get(global_idx, 100)
            opacity_float = opacity_value / 100.0
            try:
                card = create_record_card(record, global_idx, class_colors, overlay_opacity=opacity_float)
                cards.append(card)
            except Exception as e:
                import traceback
                traceback.print_exc()
                # Add error card instead
                cards.append(dbc.Card([
                    dbc.CardBody([
                        html.P(f"Error loading {record.get('image_name', 'unknown')}: {str(e)}", className="text-danger")
                    ])
                ], className="mb-3"))
        
        return (
            dbc.Alert([
                html.Strong(f"Total Images: {total}"),
                " | ",
                html.Strong(f"Filtered: {filtered_total}"),
                " | ",
                html.Strong(f"Page: {current_page + 1}/{total_pages}")
            ], color="info"),
            str(filtered_total),
            str(start_idx + 1) if page_records else "0",
            str(end_idx),
            html.Div(cards) if cards else html.Div("No records to display", className="text-center text-muted py-5"),
            current_page
        )
    
    @app.callback(
        [Output("image-modal", "is_open"),
         Output("modal-image", "src"),
         Output("modal-overlay-controls", "style"),
         Output("modal-state-store", "data"),
         Output("modal-overlay-opacity-slider", "value")],
        [Input({"type": "image-clickable", "view": ALL, "index": ALL}, "n_clicks"),
         Input("close-modal", "n_clicks"),
         Input("modal-overlay-opacity-slider", "value")],
        [State("data-store", "data"),
         State("class-colors-store", "data"),
         State("overlay-opacity-store", "data"),
         State("image-modal", "is_open"),
         State("modal-state-store", "data")],
        prevent_initial_call=True
    )
    def toggle_image_modal(n_clicks_list, close_clicks, slider_value, data_store, class_colors, opacity_store, is_open, modal_state):
        """Handle image modal opening/closing with overlay controls"""
        
        ctx = callback_context
        if not ctx.triggered:
            return False, "", {"display": "none"}, modal_state or {'view': None, 'index': None}, 100
        
        trigger = ctx.triggered[0]['prop_id']
        trigger_value = ctx.triggered[0]['value']
        modal_state = modal_state or {'view': None, 'index': None}
        
        # Close modal
        if "close-modal" in trigger:
            return False, "", {"display": "none"}, {'view': None, 'index': None}, 100
        
        # Handle overlay opacity slider change
        if "modal-overlay-opacity-slider" in trigger:
            if slider_value is None:
                return is_open, "", {"display": "none"}, modal_state, 100
            # Get current modal state to know which image we're viewing
            view = modal_state.get('view')
            index = modal_state.get('index')
            
            if view != 'overlay' or index is None:
                return is_open, "", {"display": "none"}, modal_state, slider_value or 100
            
            if not data_store or 'data' not in data_store:
                return is_open, "", {"display": "none"}, modal_state, slider_value or 100
            
            data = data_store['data']
            if index >= len(data):
                return is_open, "", {"display": "none"}, modal_state, slider_value or 100
            
            record = data[index]
            image_path = record['image_path']
            label_data = record.get('label_data')
            
            if not label_data:
                return is_open, "", {"display": "none"}, modal_state, slider_value or 100
            
            # Update opacity store
            opacity_store = opacity_store or {}
            opacity_store[index] = slider_value
            
            # Regenerate image with new opacity
            try:
                img = Image.open(image_path)
                max_modal_size = 1200
                width, height = img.size
                if width > max_modal_size or height > max_modal_size:
                    scale = min(max_modal_size / width, max_modal_size / height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                processor = MaskProcessor()
                opacity_float = slider_value / 100.0
                overlay_img, _ = processor.create_mask_overlay(img, label_data, class_colors or {}, opacity=opacity_float)
                img_b64 = pil_to_base64(overlay_img)
                
                return is_open, img_b64, {"display": "block", "marginLeft": "20px", "minWidth": "350px"}, modal_state, slider_value
            except Exception as e:
                return is_open, "", {"display": "none"}, modal_state, slider_value or 100
        
        # Open modal with clicked image
        if "image-clickable" in trigger:
            import json
            try:
                # Parse the trigger ID to get view and index
                trigger_id_str = trigger.split('.')[0]
                trigger_dict = json.loads(trigger_id_str)
                view = trigger_dict.get('view')
                index = trigger_dict.get('index')
                
                # Check if this is actually a click (n_clicks should be > 0)
                # Note: trigger_value might be None on first render, so we check if it's a valid click
                if trigger_value is None:
                    return is_open, "", {"display": "none"}, modal_state, 100
                
                # Store modal state
                new_modal_state = {'view': view, 'index': index}
                
                if not data_store or 'data' not in data_store:
                    return False, "", {"display": "none"}, new_modal_state, 100
                
                data = data_store['data']
                filtered_data = data
                
                if index >= len(filtered_data):
                    return False, "", {"display": "none"}, new_modal_state, 100
                
                record = filtered_data[index]
                image_path = record['image_path']
                label_data = record.get('label_data')
                
                # Load and process image based on view type
                img = Image.open(image_path)
                
                # Resize for modal if too large (max 1200px for modal view)
                max_modal_size = 1200
                width, height = img.size
                if width > max_modal_size or height > max_modal_size:
                    scale = min(max_modal_size / width, max_modal_size / height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                processor = MaskProcessor()
                
                # Get opacity for this record from store
                opacity_store = opacity_store or {}
                opacity_value = opacity_store.get(index, 100)
                opacity_float = opacity_value / 100.0
                
                # Set overlay controls visibility based on view type
                controls_style = {"display": "none"}
                if view == 'overlay' and label_data:
                    # Show overlay opacity slider in header
                    controls_style = {"display": "block", "marginLeft": "20px", "minWidth": "350px"}
                
                if view == 'original':
                    display_img = img
                elif view == 'mask':
                    if label_data:
                        _, mask_img = processor.create_mask_overlay(img, label_data, class_colors or {}, opacity=opacity_float)
                        display_img = mask_img
                    else:
                        display_img = Image.new('RGB', img.size, (0, 0, 0))
                else:  # overlay
                    if label_data:
                        overlay_img, _ = processor.create_mask_overlay(img, label_data, class_colors or {}, opacity=opacity_float)
                        display_img = overlay_img
                    else:
                        display_img = img
                
                # Convert to base64
                img_b64 = pil_to_base64(display_img)
                
                return True, img_b64, controls_style, new_modal_state, opacity_value
            except Exception as e:
                return False, "", {"display": "none"}, {'view': None, 'index': None}, 100
        
        return False, "", {"display": "none"}, modal_state, 100
    
    @app.callback(
        Output('overlay-opacity-store', 'data'),
        Input("modal-overlay-opacity-slider", "value"),
        [State('overlay-opacity-store', 'data'),
         State("modal-state-store", "data")],
        prevent_initial_call=True
    )
    def update_opacity_store_from_modal(slider_value, opacity_store, modal_state):
        """Update opacity store when modal slider changes"""
        if slider_value is None or modal_state is None:
            return opacity_store or {}
        
        index = modal_state.get('index')
        if index is not None:
            opacity_store = opacity_store or {}
            opacity_store[index] = slider_value
        
        return opacity_store
