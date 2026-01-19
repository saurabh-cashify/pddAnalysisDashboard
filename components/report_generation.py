"""
Report Generation Tab Component
Handles CSV generation from raw data using Redash API
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback_context, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import pandas as pd
from pathlib import Path
import os
import sys
import base64
import zipfile
import shutil
import tempfile
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent))

from utils.report_generator import ReportGenerator
from utils.threshold_handler import load_threshold_config

# =============== CONFIGURATION ===============
# Load from environment variables, fallback to defaults for local development
API_KEY = os.getenv("REDASH_API_KEY", "IY2HlHUAz3ZX0Y1p2rg4vaFciUOV0MIlkJT0eyOe")
QUERY_ID = int(os.getenv("REDASH_QUERY_ID", "4261"))
BASE_URL = os.getenv("REDASH_BASE_URL", "http://redash.prv.api.cashify.in")
MODE = os.getenv("REDASH_MODE", "qc_automation")
BACK_KEY = os.getenv("BACK_KEY", "backmerged")
FRONT_KEY = os.getenv("FRONT_KEY", "whiterotatedmerged")
# =======================================================


def create_report_generation_tab():
    """Create the Report Generation tab layout"""
    
    threshold_config = load_threshold_config()
    question_options = [{'label': k, 'value': k} for k in threshold_config.keys() if k != 'default']
    
    return dbc.Container([
        html.Div([
            html.H2("📊 Report Generation", className="section-title"),
            html.P("Generate analysis CSV from raw data using Redash API", className="section-subtitle"),
        ], className="section-header"),
        
        dbc.Card([
            dbc.CardHeader("Configuration"),
            dbc.CardBody([
                # Commented out - hardcoded API settings
                # dbc.Row([
                #     dbc.Col([
                #         dbc.Label("Redash API Key", html_for="api-key"),
                #         dbc.Input(
                #             id="api-key",
                #             type="text",
                #             placeholder="Enter API Key",
                #             value=API_KEY
                #         ),
                #     ], md=6),
                #     dbc.Col([
                #         dbc.Label("Query ID", html_for="query-id"),
                #         dbc.Input(
                #             id="query-id",
                #             type="number",
                #             placeholder="4261",
                #             value=QUERY_ID
                #         ),
                #     ], md=6),
                # ], className="mb-3"),
                # 
                # dbc.Row([
                #     dbc.Col([
                #         dbc.Label("Base URL", html_for="base-url"),
                #         dbc.Input(
                #             id="base-url",
                #             type="text",
                #             placeholder="http://redash.prv.api.cashify.in",
                #             value=BASE_URL
                #         ),
                #     ], md=6),
                #     dbc.Col([
                #         dbc.Label("Mode", html_for="mode"),
                #         dbc.Input(
                #             id="mode",
                #             type="text",
                #             placeholder="qc_automation",
                #             value=MODE
                #         ),
                #     ], md=6),
                # ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Question Name", html_for="question-name"),
                        dcc.Dropdown(
                            id="question-name",
                            options=question_options,
                            value=question_options[0]['value'] if question_options else None,
                            placeholder="Select question",
                            style={"color": "#000"},
                            persistence=True,
                            persistence_type='session'
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Output Folder Name", html_for="output-folder"),
                        dbc.Input(
                            id="output-folder",
                            type="text",
                            placeholder="analysis_YYYY_MM_DD",
                            value=f"analysis_{datetime.now().strftime('%Y_%m_%d')}"
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Source", html_for="source-select"),
                        dcc.Dropdown(
                            id="source-select",
                            options=[
                                {'label': 'Cscanpro-Line2', 'value': 'Cscanpro-Line2'},
                                {'label': 'Cscanpro-Line3', 'value': 'Cscanpro-Line3'}
                            ],
                            value='Cscanpro-Line2',
                            placeholder="Select source",
                            style={"color": "#000"},
                            persistence=True,
                            persistence_type='session'
                        ),
                    ], md=4),
                ], className="mb-3"),
            ])
        ], className="mb-4"),
        
        dbc.Card([
            dbc.CardHeader("Input Files"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Raw Data CSV", html_for="raw-data-upload"),
                        dcc.Upload(
                            id="raw-data-upload",
                            children=html.Div([
                                html.Div([
                                    html.I(className="fas fa-file-csv", style={"fontSize": "3em", "color": "#3b82f6", "marginBottom": "15px"}),
                                ]),
                                html.Div([
                                    html.Span("Drag and Drop or ", style={"color": "#64748b", "fontSize": "1.1em", "fontWeight": "500"}),
                                    html.A("Select Raw Data CSV", style={"color": "#3b82f6", "textDecoration": "underline", "fontWeight": "600"})
                                ])
                            ]),
                            style={
                                'width': '100%',
                                'minHeight': '120px',
                                'border': '2px dashed #3b82f6',
                                'borderRadius': '12px',
                                'padding': '30px',
                                'textAlign': 'center',
                                'background': 'linear-gradient(to bottom, #f8fafc, #f1f5f9)',
                                'cursor': 'pointer',
                                'display': 'flex',
                                'flexDirection': 'column',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'transition': 'all 0.3s ease'
                            },
                            multiple=False
                        ),
                        html.Div(id="raw-data-filename", className="mt-2"),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Analysis Folder", html_for="eval-folder-input"),
                        html.Div([
                            html.Div(
                                id="eval-folder-upload-area",
                                children=[
                                    html.Div([
                                        html.I(className="fas fa-folder-open", style={"fontSize": "3em", "color": "#3b82f6", "marginBottom": "15px"}),
                                    ]),
                                    html.Div([
                                        html.Span("Click to ", style={"color": "#64748b", "fontSize": "1.1em", "fontWeight": "500"}),
                                        html.A("Select Analysis Folder", style={"color": "#3b82f6", "textDecoration": "underline", "fontWeight": "600"})
                                    ]),
                                    html.Small("Folder with analysis CSV + eval subfolder", className="text-muted d-block mt-2")
                                ],
                                style={
                                    'width': '100%',
                                    'minHeight': '120px',
                                    'border': '2px dashed #3b82f6',
                                    'borderRadius': '12px',
                                    'padding': '30px',
                                    'textAlign': 'center',
                                    'background': 'linear-gradient(to bottom, #f8fafc, #f1f5f9)',
                                    'cursor': 'pointer',
                                    'display': 'flex',
                                    'flexDirection': 'column',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'transition': 'all 0.3s ease'
                                }
                            ),
                            # Hidden file input for folder selection
                            dcc.Upload(
                                id="eval-folder-upload",
                                children=html.Div(),
                                style={'display': 'none'},
                                multiple=True
                            ),
                        ]),
                        html.Div(id="eval-folder-filename", className="mt-2"),
                        # Store to track folder selection
                        dcc.Store(id="folder-selection-trigger", data=0),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Analysis CSV", html_for="analysis-csv-upload"),
                        dcc.Upload(
                            id="analysis-csv-upload",
                            children=html.Div([
                                html.Div([
                                    html.I(className="fas fa-file-invoice", style={"fontSize": "3em", "color": "#10b981", "marginBottom": "15px"}),
                                ]),
                                html.Div([
                                    html.Span("Drag and Drop or ", style={"color": "#64748b", "fontSize": "1.1em", "fontWeight": "500"}),
                                    html.A("Select Analysis CSV", style={"color": "#10b981", "textDecoration": "underline", "fontWeight": "600"})
                                ])
                            ]),
                            style={
                                'width': '100%',
                                'minHeight': '120px',
                                'border': '2px dashed #10b981',
                                'borderRadius': '12px',
                                'padding': '30px',
                                'textAlign': 'center',
                                'background': 'linear-gradient(to bottom, #f0fdf4, #dcfce7)',
                                'cursor': 'pointer',
                                'display': 'flex',
                                'flexDirection': 'column',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'transition': 'all 0.3s ease'
                            },
                            multiple=False
                        ),
                        html.Small("Skip generation - use existing analysis CSV", className="text-muted d-block mt-2"),
                        html.Div(id="analysis-csv-filename", className="mt-2"),
                    ], md=4),
                ]),
            ])
        ], className="mb-4"),
        
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "🔄 Reset Data",
                            id="reset-data-btn",
                            color="warning",
                            size="lg",
                            className="w-100",
                            n_clicks=0
                        ),
                    ], md=5),
                    dbc.Col([
                        dbc.Button(
                            "🚀 Generate Report",
                            id="generate-report-btn",
                            color="primary",
                            size="lg",
                            className="w-100 download-button",
                            n_clicks=0
                        ),
                    ], md=5),
                ], className="g-3 justify-content-center"),
                dcc.Loading(
                    id="loading-generation",
                    type="default",
                    children=html.Div(id="generation-status", className="mt-3")
                ),
                # Download button (hidden until ready)
                html.Div(id="download-button-container", className="mt-3"),
                dcc.Store(id="generated-csv-path", data=None),
                dcc.Store(id="generated-folder-path", data=None),
                dcc.Download(id="download-folder"),  # Direct download without intermediate button
            ])
        ], className="mb-4"),
        
    ], fluid=True, className="tab-content-container")


def register_report_generation_callbacks(app):
    """Register callbacks for report generation tab"""
    
    # Reset data store when reset button is clicked
    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Input("reset-data-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_data_store(n_clicks):
        """Clear data-store when reset button is clicked"""
        if n_clicks and n_clicks > 0:
            return {}
        from dash import no_update
        return no_update
    
    @app.callback(
        Output("raw-data-filename", "children"),
        Input("raw-data-upload", "contents"),
        State("raw-data-upload", "filename")
    )
    def update_raw_data_filename(contents, filename):
        if contents is not None:
            return html.Div([
                html.I(className="fas fa-check-circle text-success me-2"),
                f"File loaded: {filename}"
            ], style={"color": "#10b981", "fontWeight": "500"})
        return ""
    
    @app.callback(
        Output("analysis-csv-filename", "children"),
        Input("analysis-csv-upload", "contents"),
        State("analysis-csv-upload", "filename")
    )
    def update_analysis_csv_filename(contents, filename):
        if contents is not None:
            return html.Div([
                html.I(className="fas fa-check-circle text-success me-2"),
                f"Analysis CSV loaded: {filename}"
            ], style={"color": "#10b981", "fontWeight": "500"})
        return ""
    
    @app.callback(
        Output("eval-folder-filename", "children"),
        Input("eval-folder-upload", "contents"),
        State("eval-folder-upload", "filename")
    )
    def update_eval_folder_filename(contents, filename):
        if contents is not None and isinstance(contents, list):
            # Get folder name from first file path if available
            folder_name = "Unknown"
            if filename and len(filename) > 0:
                # Extract folder name from first file's path
                first_path = filename[0]
                if '/' in first_path:
                    folder_name = first_path.split('/')[0]
            
            return html.Div([
                html.I(className="fas fa-check-circle text-success me-2"),
                f"Folder loaded: {folder_name} ({len(contents)} files)"
            ], style={"color": "#10b981", "fontWeight": "500"})
        return ""
    
    @app.callback(
        [Output("generation-status", "children"),
         Output("download-button-container", "children"),
         Output("data-store", "data", allow_duplicate=True),  # Direct output to data-store
         Output("generated-folder-path", "data"),
         Output("download-folder", "data")],  # Direct download output
        Input("generate-report-btn", "n_clicks"),
        [State("question-name", "value"),
         State("output-folder", "value"),
         State("source-select", "value"),
         State("raw-data-upload", "contents"),
         State("raw-data-upload", "filename"),
         State("analysis-csv-upload", "contents"),
         State("analysis-csv-upload", "filename"),
         State("eval-folder-upload", "contents"),
         State("eval-folder-upload", "filename")],
        prevent_initial_call=True
    )
    def generate_report(
        n_clicks,
        question_name,
        output_folder, source,
        raw_data_contents, raw_data_filename,
        analysis_csv_contents, analysis_csv_filename,
        eval_folder_contents, eval_folder_filename
    ):
        if not n_clicks or n_clicks == 0:
            raise PreventUpdate
        
        # Get back_key and front_key from environment variables
        back_key = BACK_KEY
        front_key = FRONT_KEY
        
        # Validation
        if not all([question_name, back_key, front_key, output_folder]):
            return dbc.Alert("Please fill in all required configuration fields", color="warning"), "", None, None, None
        
        # Check if folder with analysis CSV is provided
        folder_has_analysis_csv = False
        if eval_folder_contents and isinstance(eval_folder_contents, list) and eval_folder_filename:
            # Check if any file is an analysis CSV
            for fname in eval_folder_filename:
                if fname and 'analysis_' in fname.lower() and fname.endswith('.csv'):
                    folder_has_analysis_csv = True
                    break
        
        # Check if either raw data (for generation), analysis CSV (direct), or folder with analysis CSV is provided
        if raw_data_contents is None and analysis_csv_contents is None and not folder_has_analysis_csv:
            return dbc.Alert("Please upload either a Raw Data CSV (for generation), an Analysis CSV (direct), or a Folder containing analysis CSV", color="warning"), "", None, None, None
        
        # Determine mode
        # Priority: folder update > direct analysis > generation
        use_folder_update = folder_has_analysis_csv
        use_direct_analysis = analysis_csv_contents is not None and not use_folder_update
        use_generation = raw_data_contents is not None and not use_folder_update and not use_direct_analysis
        
        try:
            # Create temporary directory for processing
            temp_dir = tempfile.mkdtemp()
            analysis_csv_path = None
            temp_raw_file = None
            uploaded_threshold_json = None
            
            # Handle folder update mode (folder with analysis CSV + eval + threshold.json)
            if use_folder_update:
                # Will process folder contents below
                pass
            
            # Handle direct analysis CSV upload
            elif use_direct_analysis:
                # Parse and save analysis CSV directly
                content_type, content_string = analysis_csv_contents.split(',')
                decoded = base64.b64decode(content_string)
                analysis_csv_path = os.path.join(temp_dir, analysis_csv_filename)
                with open(analysis_csv_path, 'wb') as f:
                    f.write(decoded)
            
            # Handle generation mode
            elif use_generation:
                # Step 1: Parse and save raw data CSV (for generation)
                content_type, content_string = raw_data_contents.split(',')
                decoded = base64.b64decode(content_string)
                temp_raw_file = os.path.join(temp_dir, raw_data_filename)
                with open(temp_raw_file, 'wb') as f:
                    f.write(decoded)
            
            # Process analysis folder if provided (folder with multiple files)
            eval_path = None
            
            if eval_folder_contents and isinstance(eval_folder_contents, list):
                # Multiple files uploaded (folder contents)
                eval_extract_path = os.path.join(temp_dir, "uploaded_folder")
                os.makedirs(eval_extract_path, exist_ok=True)
                
                # Save each file maintaining folder structure
                for idx, (content, fname) in enumerate(zip(eval_folder_contents, eval_folder_filename)):
                    # Skip if content is None or empty
                    if not content:
                        continue
                    
                    try:
                        content_type, content_string = content.split(',')
                        decoded = base64.b64decode(content_string)
                        
                        # Create subdirectories if needed (preserving folder structure)
                        file_path = os.path.join(eval_extract_path, fname)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        with open(file_path, 'wb') as f:
                            f.write(decoded)
                    except Exception as e:
                        print(f"⚠️  Error saving {fname}: {e}")
                        continue
                
                # Look for eval folder, analysis CSV, and threshold.json
                eval_csv_folder = None
                found_analysis_csv = None
                found_threshold_json = None
                eval_csv_files = []  # Track eval CSV files
                
                for root, dirs, files in os.walk(eval_extract_path):
                    # Look for 'eval' subfolder
                    if 'eval' in dirs:
                        eval_csv_folder = os.path.join(root, 'eval')
                    
                    # Check for files at root level
                    for file in files:
                        # Look for analysis CSV (only in folder update mode)
                        if file.startswith('analysis_') and file.endswith('.csv') and use_folder_update:
                            found_analysis_csv = os.path.join(root, file)
                        
                        # Look for threshold.json
                        if file.lower() == 'threshold.json':
                            found_threshold_json = os.path.join(root, file)
                        
                        # Track CSV files that might be eval results (numeric names)
                        if file.endswith('.csv') and not file.startswith('analysis_'):
                            eval_csv_files.append(os.path.join(root, file))
                
                # If eval folder exists, use it
                eval_path = eval_csv_folder
                
                # If no eval folder but we have numeric CSV files, create a synthetic eval folder
                if not eval_path and eval_csv_files:
                    # Check if CSV files are in a subfolder
                    for csv_file in eval_csv_files:
                        csv_dir = os.path.dirname(csv_file)
                        if csv_dir != eval_extract_path:
                            # CSVs are in a subfolder
                            eval_path = csv_dir
                            break
                    
                    # If all CSVs are at root level, infer they're eval CSVs and move them to eval folder
                    if not eval_path and use_folder_update:
                        synthetic_eval_path = os.path.join(eval_extract_path, "eval")
                        os.makedirs(synthetic_eval_path, exist_ok=True)
                        
                        # Move numeric CSV files to eval folder
                        import shutil
                        for csv_file in eval_csv_files:
                            if os.path.dirname(csv_file) == eval_extract_path:
                                # File is at root, move to eval
                                new_path = os.path.join(synthetic_eval_path, os.path.basename(csv_file))
                                shutil.move(csv_file, new_path)
                        
                        eval_path = synthetic_eval_path
                
                # In folder update mode, use found analysis CSV
                if use_folder_update and found_analysis_csv:
                    analysis_csv_path = found_analysis_csv
                
                # Use found threshold.json if available
                if found_threshold_json:
                    uploaded_threshold_json = found_threshold_json
            
            # Create output folder structure in temp
            output_folder_name = output_folder or f"analysis_{datetime.now().strftime('%Y_%m_%d')}"
            output_path = os.path.join(temp_dir, output_folder_name)
            os.makedirs(output_path, exist_ok=True)
            os.makedirs(os.path.join(output_path, "eval"), exist_ok=True)
            
            # Generate or use/update analysis CSV
            if use_folder_update:
                # Folder update mode: load analysis CSV, join with eval, create new_cscan_answer
                import shutil
                
                # Initialize generator with uploaded threshold if available
                generator = ReportGenerator(
                    api_key=API_KEY,
                    query_id=QUERY_ID,
                    base_url=BASE_URL,
                    question_name=question_name,
                    back_key=back_key,
                    front_key=front_key,
                    mode=MODE,
                    threshold_path=uploaded_threshold_json  # Use uploaded threshold if available
                )
                
                # Load existing analysis CSV
                df_analysis = pd.read_csv(analysis_csv_path)
                print(f"📊 Loaded analysis CSV: {len(df_analysis)} rows")
                
                # Join with eval results if eval folder exists
                if eval_path and os.path.exists(eval_path):
                    print("🔗 Joining with eval results...")
                    df_analysis = generator.join_with_eval_results(df_analysis, eval_path)
                    
                    # Sort by quote_date before calculating new_acc%
                    if 'quote_date' in df_analysis.columns:
                        print("📅 Sorting by quote_date...")
                        df_analysis = df_analysis.sort_values(by='quote_date', na_position='last')
                    
                    # Create new_cscan_answer and new_contributing_sides
                    print("🔍 Creating new_cscan_answer and new_contributing_sides...")
                    df_analysis = generator.create_new_cscan_answer(df_analysis)
                    
                    # Calculate new_acc%
                    print("📊 Calculating new_acc%...")
                    df_analysis = generator.calculate_accuracy(df_analysis, 'new_cscan_answer', 'new_acc%')
                    
                    # Create confusion matrices
                    print("📊 Creating confusion matrices...")
                    generator.create_confusion_matrices(df_analysis, output_path)
                
                # Reorder columns for updated CSV (with new_* columns)
                print("📋 Reordering columns...")
                df_analysis = generator.reorder_columns(df_analysis, include_new_columns=True)
                
                # Save updated CSV
                final_csv_path = os.path.join(output_path, f"analysis_{datetime.now().strftime('%Y_%m_%d')}.csv")
                df_analysis.to_csv(final_csv_path, index=False)
                csv_path = final_csv_path
                print(f"✅ Updated analysis CSV saved: {csv_path}")
                
            elif use_direct_analysis:
                # Direct analysis mode: just copy the CSV
                import shutil
                final_csv_path = os.path.join(output_path, f"analysis_{datetime.now().strftime('%Y_%m_%d')}.csv")
                shutil.copy(analysis_csv_path, final_csv_path)
                csv_path = final_csv_path
                
                # Try to generate UUID JSONs and confusion matrices if data is available
                try:
                    df_analysis = pd.read_csv(csv_path)
                    
                    # Initialize generator for UUID and confusion matrix generation
                    generator = ReportGenerator(
                        api_key=API_KEY,
                        query_id=QUERY_ID,
                        base_url=BASE_URL,
                        question_name=question_name,
                        back_key=back_key,
                        front_key=front_key,
                        mode=MODE
                    )
                    
                    # Generate UUID JSONs (will use data from the CSV)
                    generator._create_uuid_jsons(df_analysis, output_path)
                    
                    # Generate confusion matrices
                    generator._create_confusion_matrix(df_analysis, output_path)
                    generator._create_comparison_confusion_matrix(df_analysis, output_path)
                except Exception as e:
                    print(f"⚠️  Warning: Could not generate UUID JSONs or confusion matrices: {e}")
            else:
                # Generation mode: fetch from Redash and generate full report
                generator = ReportGenerator(
                    api_key=API_KEY,
                    query_id=QUERY_ID,
                    base_url=BASE_URL,
                    question_name=question_name,
                    back_key=back_key,
                    front_key=front_key,
                    mode=MODE
                )
                
                # Generate report (this will take time)
                csv_path = generator.generate_report(
                    raw_data_path=temp_raw_file,
                    output_folder=output_path,
                    eval_folder=eval_path,
                    include_eval=eval_path is not None,
                    source=source if source else "Cscanpro-Line2"
                )
            
            # Load CSV data for auto-loading in other tabs
            df = pd.read_csv(csv_path)
            csv_data_dict = df.to_dict('records')
            csv_columns = list(df.columns)
            
            # Store CSV data (not path, since temp will be deleted)
            # Store as dict with metadata for other tabs
            source_mode = "folder_update" if use_folder_update else ("direct" if use_direct_analysis else "generated")
            csv_data_for_store = {
                "data": csv_data_dict,
                "columns": csv_columns,
                "source": source_mode,
                "folder_name": output_folder_name,
                "question_name": question_name  # Store question name from report generation
            }
            
            # Create ZIP for generation and folder update modes
            zip_data = None
            zip_filename = None
            download_info = ""
            
            if use_generation or use_folder_update:
                # Create ZIP file for download
                zip_filename = f"{output_folder_name}.zip"
                zip_path = os.path.join(temp_dir, zip_filename)
                
                # Copy threshold.json to output folder
                import shutil
                if use_folder_update and uploaded_threshold_json and os.path.exists(uploaded_threshold_json):
                    # Use uploaded threshold.json
                    shutil.copy(uploaded_threshold_json, os.path.join(output_path, 'threshold.json'))
                    print(f"   ✓ Copied uploaded threshold.json to output")
                else:
                    # Use default threshold.json
                    threshold_json_path = os.path.join(os.path.dirname(__file__), '..', 'threshold.json')
                    if os.path.exists(threshold_json_path):
                        shutil.copy(threshold_json_path, os.path.join(output_path, 'threshold.json'))
                        print(f"   ✓ Copied default threshold.json to output")
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add all files from output folder
                    for root, dirs, files in os.walk(output_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_path)
                            zipf.write(file_path, arcname)
                
                # Read ZIP file for download
                with open(zip_path, 'rb') as f:
                    zip_data = base64.b64encode(f.read()).decode()
                
                # Download info message (download will start automatically)
                download_info = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-download me-2"),
                        html.Span("📥 Your download will start automatically...")
                    ], className="d-flex align-items-center"),
                    html.Small(f"File: {zip_filename}", className="text-muted d-block mt-2")
                ], color="info", className="mt-2")
            
            # Success message
            if use_folder_update:
                mode_text = "Folder Processed & Updated"
                success_msg = dbc.Alert([
                    html.H4(f"✅ {mode_text} Successfully!", className="alert-heading"),
                    html.P("Analysis CSV updated with eval results, new scores, and confusion matrices."),
                    html.P([
                        html.Small(
                            f"Processed {len(csv_data_dict)} records with {len(csv_columns)} columns. Data auto-loaded in other tabs.",
                            className="text-muted"
                        )
                    ], className="mt-2")
                ], color="success")
            elif use_direct_analysis:
                mode_text = "Analysis Loaded"
                success_msg = dbc.Alert([
                    html.H4(f"✅ {mode_text} Successfully!", className="alert-heading"),
                    html.P("Data loaded and ready for analysis."),
                    html.P([
                        html.Small(
                            f"Loaded {len(csv_data_dict)} records with {len(csv_columns)} columns. View data in other tabs.",
                            className="text-muted"
                        )
                    ], className="mt-2")
                ], color="success")
            else:
                mode_text = "Report Generated"
                success_msg = dbc.Alert([
                    html.H4(f"✅ {mode_text} Successfully!", className="alert-heading"),
                    html.P("Your analysis folder is ready for download."),
                    html.P([
                        html.Small(
                            f"Generated {len(csv_data_dict)} records with {len(csv_columns)} columns. Data auto-loaded in other tabs.",
                            className="text-muted"
                        )
                    ], className="mt-2")
                ], color="success")
            
            # Clean up temp directory
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            # Debug print
            mode_name = "Folder Update" if use_folder_update else ("Direct Analysis" if use_direct_analysis else "Generation")
            print(f"\n✅ Report generation complete:")
            print(f"   - Mode: {mode_name}")
            print(f"   - Records: {len(csv_data_dict)}")
            print(f"   - Columns: {len(csv_columns)}")
            print(f"   - Source: {csv_data_for_store.get('source', 'unknown')}")
            print(f"   - Auto-loading data to all tabs...")
            if zip_data:
                print(f"   - Downloading ZIP: {zip_filename} ({len(zip_data)} bytes)")
            
            # Return success (5 outputs: status, download info, csv data, folder name, download dict)
            if use_direct_analysis:
                # Direct mode: no download
                from dash import no_update
                return success_msg, download_info, csv_data_for_store, output_folder_name, no_update
            else:
                # Generation and Folder Update modes: trigger download
                return success_msg, download_info, csv_data_for_store, output_folder_name, dict(
                    content=zip_data,
                    filename=zip_filename,
                    base64=True
                )
            
        except Exception as e:
            import traceback
            error_msg = dbc.Alert([
                html.H4("❌ Error Generating Report", className="alert-heading"),
                html.P(str(e)),
                html.Pre(traceback.format_exc(), className="small", style={"whiteSpace": "pre-wrap", "maxHeight": "300px", "overflow": "auto"})
            ], color="danger")
            # Return error message, empty download info, no data, no folder name, no download
            from dash import no_update
            return error_msg, "", None, None, no_update
    
    # Note: Auto-load CSV callback is handled in app.py to access data-store
    # Download happens automatically from the main callback above (no separate button callback needed)
0