# Analysis Dashboard - Dash Framework Version

## Overview

This is a comprehensive analysis dashboard for Physical Condition Detection (Scratch/Panel) built with Dash framework. The dashboard provides interactive visualizations, threshold tweaking capabilities, and detailed analysis tools for model performance evaluation.

## Features

### ✅ All Features Implemented

1. **📊 Report Generation Tab**
   - Upload raw data CSV files
   - Configure Redash API settings for query execution
   - Select question name from threshold.json (physicalConditionScratch, physicalConditionPanel, etc.)
   - Configure back/front image keys
   - Optional eval folder integration
   - Generates complete analysis CSV with all calculations
   - Creates confusion matrix PNG images with date-based titles
   - Output folder naming: `analysis_YYYY_MM_DD` (date-based only)
   - Reset Data button to clear loaded data
   - Support for direct analysis CSV upload (folder update mode)
   - Automatic threshold.json detection from uploaded folders

2. **📈 Analytics Tab**
   - Performance Overview Cards (Total Records, Accuracy, Agreement Rate)
   - Day-wise Performance Trend chart (grouped by quote_date)
   - Model Comparison Metrics Table (with CSV export)
   - Category Performance Breakdown chart
   - Error Analysis chart
   - Performance by Side chart
   - Score Distribution Comparison charts
   - Agreement Analysis chart

3. **📊 Confusion Matrices Tab**
   - Dual matrix view (Deployed Model vs New Model)
   - Clickable cells for detailed analysis
   - Real-time accuracy metrics (Accuracy % and Sample count)
   - Dynamic question name detection from report generation
   - Category normalization (e.g., "glass panel damaged" merged with "cracked or broken panel" for physicalConditionPanel)
   - Date-based matrix titles (dd/mm/yyyy format)
   - Cell detail drill-down to view filtered records

4. **📷 Image Viewer Tab**
   - Multi-filter system:
     - Deployed CScan Answer filter
     - New CScan Answer filter
     - Final Answer filter
     - Deployed Contributing Sides filter
     - New Contributing Sides filter
     - Deployed Side Score Filter (range slider + side multiselect)
     - New Side Score Filter (range slider + side multiselect)
   - Record navigation (First, Previous, Next, Last) with pagination
   - Smart Image Tab Display**: Only shows tabs for sides that have valid image URLs
     - Checks for `top_image_url`, `bottom_image_url`, `right_image_url`, `left_image_url`, `back_image_url`, `front_image_url`
     - If only `front_image_url` exists, only the front image tab is displayed
   - Front Black Image Support**: 
     - Displays both front and front_black images side-by-side when input toggle is active
     - Shows `front_black_image_url` and `front_black_uuid` alongside front images
     - Both images are clickable and open in expanded modal view
   - Image toggle (input vs result images) - record-specific
   - Side-by-side comparison (deployed vs new model)
   - Single image view (when only deployed model available)
   - Image Expansion Modal with Gamma Adjustment**:
     - Click any image to open in full-size modal
     - Gamma adjustment slider (0.1 to 3.0) in modal header
     - Real-time gamma correction using canvas-based processing
     - CSS filter fallback for CORS-restricted images
   - Expandable/collapsible rows for detailed view
   - Score badges with color coding
   - Copy Request Body button for each side
   - Export Audit CSV functionality
   - Auto-reset filters on tab switch

5. **🔍 Cell Details Tab**
   - Filtered record table from confusion matrix cell clicks
   - All filters from Image Viewer (same functionality)
   - Inline record viewer with expandable rows
   - Image gallery with toggle (input vs result)
   - Front Black Image Support**: Same as Image Viewer
   - Gamma Adjustment: Available in expanded image modal
   - Image expansion on click (modal view)
   - Answer comparison
   - Export Audit CSV functionality
   - Back to Matrix button
   - Auto-reset filters on tab switch

6. **🎛️ Threshold Tweaker Tab**
   - Model toggle (Deployed Model vs New Model)
   - Reference matrix (static baseline) with dynamic headers
   - Live-adjusted matrix with change highlighting
   - Side Selection: Back, Left, Right, Top, Bottom, Front (all 6 sides supported)
   - Side-specific threshold range sliders (integer values only)
   - Real-time impact calculation (Records Changed, Accuracy Delta, Original Accuracy)
   - Changed records viewer with full filtering capabilities
   - Optimize Thresholds button (optimizes all sides)
   - Optimize Selected Side button (optimizes currently selected side)
   - Processing loader during optimization
   - Reset to Original button
   - Dynamic question name detection from report generation
   - Category ordering from threshold.json
   - Gamma Adjustment: Available in expanded image modal

## Installation

```bash
cd /Users/saurabhsingh/Downloads/root/analysisDashboard
pip install -r requirements.txt
```

## Usage

### Starting the Dashboard

```bash
python app.py
```

The dashboard will be available at: `http://localhost:8050`

### Tab Order

The dashboard has 6 tabs in the following order:
1. 📊 Report Generation
2. 📈 Analytics
3. 📊 Confusion Matrices
4. 📷 Image Viewer
5. 🔍 Cell Details
6. 🎛️ Threshold Tweaker

## Detailed Usage Instructions

### 📊 Report Generation Tab

#### Step 1: Configure Redash API Settings
1. **API Key**: Enter your Redash API key
2. **Query ID**: Enter the Redash query ID (default: 4261)
3. **Base URL**: Enter your Redash server URL (e.g., `https://redash.example.com`)
4. **Mode**: Select query mode (default: `qc_automation`)

#### Step 2: Configure Question Settings
1. **Question Name**: Select from dropdown (options from `threshold.json`):
   - `physicalConditionScratch`
   - `physicalConditionPanel`
   - `physicalConditionDent`
   - `screenPhysicalCondition`
   - `screenDisplaySpot`
   - `screenBubblePaint`
   - `screenDisplayLines`
   - `screenDiscoloration`
   - `cameraGlassBroken`
   - Or any other question defined in `threshold.json`
2. **Back Key**: Select image key for back side:
   - Options: `backmerged`, `back`, `backcenter50`
3. **Front Key**: Select image key for front side:
   - Options: `whiterotatedmerged`, `front`, `white`

#### Step 3: Upload Data
1. **Raw Data CSV**: Click "Choose File" and select your raw data CSV file
   - Required column: `pdd_txn_id`
   - Should contain `quote_date` column (format: `dd/mm/yyyy`)
   - Should contain `front_black_image_url` and `front_black_uuid` columns (if available)
2. **Eval Folder** (Optional): Enter path to folder containing eval CSV files
   - If provided, eval files will be joined with raw data
3. **Direct Analysis CSV** (Optional): Upload analysis CSV directly for folder update mode

#### Step 4: Set Output Folder
- **Output Folder Name**: Enter name for output folder (default: `analysis_YYYY_MM_DD`)
- The folder name is date-based only (no question name suffix)

#### Step 5: Generate Report
1. Click **"Generate Report"** button
2. Wait for completion (may take 2-5 minutes for Redash query execution)
3. The generated CSV and confusion matrices will be saved in the output folder
4. Data is automatically loaded into the dashboard for use in other tabs

#### Step 6: Reset Data (Optional)
- Click **"Reset Data"** button to clear loaded data
- This will reset all tabs and require re-uploading data

### 📈 Analytics Tab

The Analytics tab automatically displays metrics based on the loaded data from Report Generation.

#### Features:
- **Performance Overview**: Cards showing total records, accuracy metrics, and agreement rate
- **Day-wise Performance Trend**: Line chart showing accuracy trends over time (grouped by `quote_date`)
- **Model Comparison Table**: Detailed metrics comparing Deployed and New models (exportable to CSV)
- **Category Performance**: Bar chart showing accuracy by category
- **Error Analysis**: Chart showing misclassification patterns
- **Performance by Side**: Chart comparing accuracy across different sides
- **Score Distribution**: Histograms comparing score distributions between models
- **Agreement Analysis**: Chart showing agreement/disagreement between models

#### Usage:
- No user interaction required - data is automatically loaded
- Click the export button on the Model Comparison table to download CSV
- Charts can be exported using Plotly's native export functionality (camera icon in toolbar)

### 📊 Confusion Matrices Tab

#### Viewing Matrices:
- Two confusion matrices are displayed side-by-side:
  - **Deployed Model** (left): Shows `cscan_answer` vs `final_answer`
  - **New Model** (right): Shows `new_cscan_answer` vs `final_answer`
- Each matrix shows:
  - Accuracy percentage
  - Total sample count
  - Color-coded cells (darker = more samples)

#### Interacting with Matrices:
1. **Click a Cell**: Clicking any cell in a confusion matrix will:
   - Filter records matching that cell's predicted and actual values
   - Navigate to the **Cell Details** tab
   - Display filtered records in the Cell Details page

2. **Understanding the Matrices**:
   - Rows represent predicted values (from model)
   - Columns represent actual values (ground truth)
   - Diagonal cells (top-left to bottom-right) = correct predictions
   - Off-diagonal cells = misclassifications

#### Matrix Titles:
- Matrices show date-based titles:
  - Single date: `Confusion Matrix: dd/mm/yyyy`
  - Multiple dates: `Confusion Matrix: dd/mm/yyyy - dd/mm/yyyy` (min - max)

### 📷 Image Viewer Tab

#### Filtering Records:
1. **Answer Filters**:
   - **Deployed CScan Answer**: Multi-select dropdown
   - **New CScan Answer**: Multi-select dropdown
   - **Final Answer**: Multi-select dropdown

2. **Contributing Sides Filters**:
   - **Deployed Contributing Sides**: Multi-select (includes "(Blank)" option)
   - **New Contributing Sides**: Multi-select (includes "(Blank)" option)

3. **Score Filters**:
   - **Deployed Side Score Filter**:
     - Range slider (0-100, integer values only)
     - Side multiselect dropdown
     - Filters records where any selected side has a score within the range
   - **New Side Score Filter**:
     - Range slider (0-100, integer values only)
     - Side multiselect dropdown
     - Only applies if new model data exists

4. **Apply Filters**: Click "🔍 Apply Filters" to filter records
5. **Reset Filters**: Click "🔄 Reset Filters" to clear all filters

#### Viewing Records:
- **Pagination**: Records are displayed 10 per page
- **Navigation**: Use First, Previous, Next, Last buttons
- **Stats Bar**: Shows total records, filtered count, current position, and accuracy metrics

#### Smart Image Tab Display:
- **Conditional Display**: Only sides with valid image URLs are shown
  - Checks for: `top_image_url`, `bottom_image_url`, `right_image_url`, `left_image_url`, `back_image_url`, `front_image_url`
  - If a side's image URL is missing, empty, or invalid, that tab is not displayed
  - Example: If only `front_image_url` exists, only the front image tab will be shown

#### Front Black Image Support:
- **When Input Toggle is Active**: Front side displays both front and front_black images side-by-side
  - Left column: Front Input image with `front_uuid`
  - Right column: Front Black Input image with `front_black_uuid`
- **Data Requirements**: 
  - `front_black_image_url`: URL for the front black input image
  - `front_black_uuid`: UUID for the front black image (generated from UUID columns if not present)
- **Both images are clickable** and open in the expanded modal view

#### Interacting with Records:
1. **Expand Row**: Click the arrow (▶) or date in the table row to expand/collapse
2. **View Images**: 
   - Each side shows deployed and new model images (if available)
   - Single image view when only deployed model is available
   - Front side shows both front and front_black when input toggle is active
3. **Toggle Image Mode**:
   - Click the "🔄 Input" or "🔄 Result" badge to toggle between input and result images
   - Toggle state is record-specific (each record maintains its own state)
   - When toggled to Input mode on front side, both front and front_black images are displayed
4. **Expand Image**: Click any image to open it in a modal for full-size viewing
5. **Gamma Adjustment** (in Modal):
   - Use the gamma slider in the modal header (range: 0.1 to 3.0)
   - Default value: 1.0 (no adjustment)
   - Values < 1.0: Brighten the image
   - Values > 1.0: Darken the image
   - Real-time adjustment using canvas-based gamma correction
6. **Score Badges**: 
   - Color-coded badges show scores for each side
   - Red = contributing side, Green = non-contributing side
7. **Copy Request Body**: Click "Copy Request Body" button below UUID to copy request body to clipboard

#### Exporting Data:
- Click **"📥 Export Audit CSV"** to export records with audit tags
- Only records that have been audited (tagged) will be exported

#### Notes:
- Filters automatically reset when switching away from the Image Viewer tab
- Image toggle states are preserved per record
- Expanded rows are preserved when toggling images (won't auto-collapse)
- Only sides with valid image URLs are displayed as tabs

### 🔍 Cell Details Tab

#### Accessing Cell Details:
- Click any cell in the Confusion Matrices tab
- The Cell Details tab will automatically open with filtered records

#### Features:
- **Same Filtering Options**: All filters from Image Viewer are available
- **Filtered Records**: Only records matching the clicked confusion matrix cell
- **Title Bar**: Shows which cell was clicked (e.g., "No Defect → Minor Scratch")
- **Back Button**: Click "← Back to Matrix" to return to Confusion Matrices tab
- **Smart Image Tab Display**: Same as Image Viewer (only shows tabs for sides with valid URLs)
- **Front Black Image Support**: Same as Image Viewer (side-by-side display in input mode)
- **Gamma Adjustment**: Available in expanded image modal

#### Interacting with Records:
- Same interaction features as Image Viewer:
  - Expand/collapse rows
  - Toggle image mode (input/result)
  - Expand images in modal with gamma adjustment
  - Copy request body
  - Export audit CSV

#### Notes:
- Filters automatically reset when switching away from the Cell Details tab
- Data is preserved when navigating back to Confusion Matrices and clicking another cell

### 🎛️ Threshold Tweaker Tab

#### Model Selection:
- Toggle between **"Deployed Model"** and **"New Model"** using buttons in the header
- Active model is highlighted in blue
- Matrices and thresholds update based on selected model

#### Viewing Matrices:
- **Reference Matrix**: Shows baseline performance with original thresholds
- **Adjusted Matrix**: Shows performance with modified thresholds
- Headers are dynamic:
  - Deployed Model: "Deployed Model (Reference Matrix)" / "Deployed Model (Adjusted Matrix)"
  - New Model: "New Model (Reference Matrix)" / "New Model (Adjusted Matrix)"
- Each matrix shows Accuracy % and Sample count below

#### Adjusting Thresholds:
1. **Select Side**: Click a side button (Back, Left, Right, Top, Bottom, **Front**)
   - All 6 sides are now supported, including Front
2. **Adjust Sliders**: 
   - Each category has a range slider (0-100, integer values only)
   - Drag handles to adjust min/max values
   - Values update in real-time
3. **View Impact**: 
   - Impact Summary shows:
     - Records Changed count
     - Accuracy Delta (difference from original)
     - Original Accuracy
   - Changed records are displayed below with full filtering options

#### Optimizing Thresholds:
1. **Optimize All Thresholds**: 
   - Click **"🎯 Optimize Thresholds"** button
   - Optimizes thresholds for all sides to maximize accuracy
   - Shows processing loader during optimization
2. **Optimize Selected Side**:
   - Select a side first (including Front)
   - Click **"🎯 Optimize Selected Side"** button
   - Optimizes thresholds only for the selected side

#### Resetting Thresholds:
- Click **"🔄 Reset to Original"** to restore original thresholds from `threshold.json`

#### Viewing Changed Records:
- Changed records are displayed by default below the threshold adjusters
- Full filtering capabilities available (same as Image Viewer)
- Shows records where the classification changed due to threshold adjustments
- **Smart Image Tab Display**: Only shows tabs for sides with valid image URLs
- **Front Black Image Support**: Same as Image Viewer (side-by-side display in input mode)
- **Gamma Adjustment**: Available in expanded image modal

#### Notes:
- Threshold adjustments are real-time (matrices update immediately)
- Optimization may take several seconds depending on data size
- Question name is automatically detected from report generation
- Front side is now fully supported in threshold adjustment

## Configuration

### Threshold Configuration (`threshold.json`)

The dashboard automatically loads `threshold.json` from the `analysisDashboard` directory (falls back to parent directory). This file defines:

- **Question-specific thresholds**: Each question (e.g., `physicalConditionScratch`, `physicalConditionPanel`) has its own thresholds
- **Side-specific categories**: Each side (top, bottom, left, right, back, **front**) has category definitions
- **Category ranges**: Each category has `[min, max]` score ranges
- **Severity ordering**: Categories are ordered by severity (used for multi-category classification)

Example structure:
```json
{
  "physicalConditionScratch": {
    "top": {
      "No Scratches": [0, 50],
      "Minor Scratch": [51, 75],
      "Major Scratch": [76, 100]
    },
    "front": {
      "No Scratches": [0, 50],
      "Minor Scratch": [51, 75],
      "Major Scratch": [76, 100]
    },
    ...
  }
}
```

### Report Generation Configuration

#### Redash API Settings:
- **API Key**: Your Redash API authentication key
- **Query ID**: The specific query ID to execute (default: 4261)
- **Base URL**: Your Redash server URL
- **Mode**: Query execution mode (default: `qc_automation`)

#### Question Configuration:
- **Question Name**: Must match a key in `threshold.json`
- **Back Key**: Image key for back side images (used in image URL construction)
- **Front Key**: Image key for front side images (used in image URL construction)

#### Input Requirements:
- **Raw Data CSV**: Must contain `pdd_txn_id` column
- **Quote Date**: Should be in `dd/mm/yyyy` format
- **Image URLs**: Should contain `{side}_image_url` columns (top, bottom, left, right, back, front)
- **Front Black Images** (Optional): Should contain `front_black_image_url` and `front_black_uuid` columns
- **Eval Folder** (Optional): Should contain CSV files matching `pdd_txn_id` values

## File Structure

```
analysisDashboard/
├── app.py                    # Main Dash application
├── components/               # Tab components
│   ├── __init__.py
│   ├── report_generation.py  # Report Generation tab
│   ├── image_viewer.py       # Image Viewer tab
│   ├── confusion_matrix.py   # Confusion Matrix tab
│   ├── analytics.py          # Analytics tab
│   ├── threshold_tweaker.py # Threshold Tweaker tab
│   └── cell_details.py       # Cell Details tab
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── threshold_handler.py  # Threshold config loading/processing
│   ├── data_loader.py        # CSV loading and matrix preparation
│   └── report_generator.py   # Report generation logic
├── assets/                   # Static assets (CSS, JavaScript)
│   ├── custom.css
│   └── folder_upload.js
├── threshold.json            # Threshold configuration file
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Dependencies

See `requirements.txt` for full list. Main dependencies:
- `dash` - Web framework
- `dash-bootstrap-components` - UI components
- `pandas` - Data manipulation
- `plotly` - Interactive visualizations
- `numpy` - Numerical operations
- `requests` - HTTP requests for Redash API
- `matplotlib` - Static plot generation
- `seaborn` - Statistical visualizations

## Complete Workflow Example

### Step 1: Generate Report
1. Navigate to **📊 Report Generation** tab
2. Configure Redash API settings:
   - Enter API Key
   - Enter Query ID (e.g., 4261)
   - Enter Base URL
   - Select Mode
3. Select Question Name (e.g., `physicalConditionScratch`)
4. Select Back Key and Front Key
5. Upload Raw Data CSV file (with `front_black_image_url` and `front_black_uuid` if available)
6. (Optional) Enter Eval Folder path
7. Review Output Folder name (default: `analysis_YYYY_MM_DD`)
8. Click **"Generate Report"**
9. Wait for completion (progress shown in status message)

### Step 2: View Analytics
1. Navigate to **📈 Analytics** tab
2. Review performance overview cards
3. Analyze day-wise performance trends
4. Compare model metrics in the comparison table
5. Export comparison table to CSV if needed
6. Review category performance and error analysis

### Step 3: Analyze Confusion Matrices
1. Navigate to **📊 Confusion Matrices** tab
2. Review both Deployed and New model matrices
3. Check accuracy metrics for each model
4. Click any cell to view detailed records
5. Note the date range in matrix titles

### Step 4: Explore Records in Image Viewer
1. Navigate to **📷 Image Viewer** tab
2. Apply filters as needed:
   - Filter by answers
   - Filter by contributing sides
   - Filter by score ranges
3. Navigate through pages of records
4. Expand rows to view detailed images
5. **Toggle to Input mode on front side** to see both front and front_black images side-by-side
6. Toggle between input and result images for other sides
7. Click images to expand in modal
8. **Adjust gamma** using the slider in the modal header for better image visibility
9. Export audit CSV if needed

### Step 5: View Cell Details
1. From Confusion Matrices tab, click a cell
2. Automatically navigates to **🔍 Cell Details** tab
3. View filtered records matching the cell
4. Apply additional filters if needed
5. View front and front_black images when input toggle is active
6. Use gamma adjustment in expanded modal
7. Export audit CSV
8. Click "← Back to Matrix" to return

### Step 6: Tweak Thresholds
1. Navigate to **🎛️ Threshold Tweaker** tab
2. Select model (Deployed or New)
3. **Select a side** (Back, Left, Right, Top, Bottom, or **Front**)
4. Modify threshold sliders for categories
5. Observe real-time impact on adjusted matrix
6. Review changed records
7. View images with front_black support and gamma adjustment
8. (Optional) Click "🎯 Optimize Thresholds" for automatic optimization
9. Click "🔄 Reset to Original" to restore defaults

## Tips and Best Practices

1. **Data Management**:
   - Use "Reset Data" button only when you want to clear all loaded data
   - Generated reports are saved in output folders for future reference
   - Confusion matrix PNGs are saved with date-based titles
   - Ensure `front_black_image_url` and `front_black_uuid` columns are included in CSV for front black image support

2. **Filtering**:
   - Filters reset automatically when switching tabs (except Report Generation)
   - Use "Reset Filters" to clear all filters quickly
   - Score filters only apply when range is not default [0, 100] OR when specific sides are selected

3. **Image Viewing**:
   - Image toggle states are preserved per record
   - Expanded rows stay expanded when toggling images
   - Click images to view in full-size modal
   - **Use gamma adjustment** to improve image visibility (especially for dark images)
   - Only sides with valid image URLs are displayed as tabs
   - Front side shows both front and front_black images when input toggle is active

4. **Front Black Images**:
   - Front black images only display when:
     - Side is 'front'
     - Input toggle is active
     - `front_black_image_url` exists and is valid
   - Both front and front_black images are clickable and support gamma adjustment
   - UUIDs are displayed below each image

5. **Threshold Tweaking**:
   - Start with small adjustments to see impact
   - Use optimization buttons for data-driven threshold selection
   - Review changed records to understand impact
   - Reset to original if adjustments don't improve accuracy
   - **Front side is now fully supported** - adjust thresholds for front side categories

6. **Gamma Adjustment**:
   - Use gamma < 1.0 to brighten dark images
   - Use gamma > 1.0 to darken bright images
   - Default gamma = 1.0 (no adjustment)
   - Adjustment is real-time and applies to all images in modal
   - Canvas-based correction provides accurate gamma adjustment

7. **Performance**:
   - Large datasets may take time to load
   - Optimization can take 10-30 seconds depending on data size
   - Pagination helps manage large record sets (10 per page)
   - Gamma adjustment uses canvas processing (may be slower for very large images)

## Troubleshooting

### Common Issues:

1. **"No data loaded" message**:
   - Ensure you've generated a report first
   - Check that the CSV file was generated successfully
   - Try clicking "Reset Data" and regenerating the report

2. **Filters not working**:
   - Click "Apply Filters" button after setting filter values
   - Check that filter values match data format (case-sensitive)
   - Reset filters and try again

3. **Images not displaying**:
   - Verify image URLs are correct in the CSV
   - Check that image keys (back/front) are configured correctly
   - Ensure images are accessible at the URL locations
   - **Check that image URL columns exist** - only sides with valid URLs will show tabs

4. **Front black images not showing**:
   - Verify `front_black_image_url` column exists in CSV
   - Ensure input toggle is active (not result mode)
   - Check that `front_black_image_url` values are not empty or invalid
   - Verify `front_black_uuid` column exists (will use 'N/A' if missing)

5. **Gamma slider not visible**:
   - Ensure you've clicked an image to open the modal
   - Check that the modal header is visible
   - Refresh the page if slider doesn't appear

6. **Threshold tweaker not showing matrices**:
   - Ensure data has been loaded from report generation
   - Check that the selected model has data (new_cscan_answer for New Model)
   - Verify threshold.json is in the correct location
   - **Ensure Front side is defined in threshold.json** for the selected question

7. **Optimization not working**:
   - Ensure sufficient data is available
   - Check console for error messages
   - Try optimizing a single side first

8. **Some image tabs missing**:
   - This is expected behavior - only sides with valid image URLs are displayed
   - Check that `{side}_image_url` columns exist and contain valid URLs
   - Empty, null, or placeholder values will hide that side's tab

## Notes

- **Modular Architecture**: All components are separated into modules for easy maintenance
- **Threshold Integration**: Uses threshold.json instead of hardcoded values
- **Dynamic Question Detection**: Question name is automatically detected from report generation
- **Category Normalization**: Special handling for certain categories (e.g., "glass panel damaged" merged with "cracked or broken panel" for physicalConditionPanel)
- **Date Format**: Quote dates should be in `dd/mm/yyyy` format
- **Integer Scores**: All score sliders and filters use integer values only
- **State Management**: Image toggle states, expanded rows, and filters are managed per record/tab
- **Smart Tab Display**: Only shows image tabs for sides with valid image URLs
- **Front Black Support**: Front side displays both front and front_black images when input toggle is active
- **Gamma Correction**: Canvas-based gamma adjustment with CSS filter fallback for CORS issues
- **Front Side Support**: Fully supported in Threshold Tweaker (all 6 sides: top, bottom, left, right, back, front)
- **Extensible**: Easy to add new features or modify existing ones

## Recent Updates

### Version Updates:
- ✅ **Front Side Support**: Added front side to Threshold Tweaker side selector
- ✅ **Front Black Images**: Support for `front_black_image_url` and `front_black_uuid` columns
- ✅ **Smart Tab Display**: Conditional display of image tabs based on available image URLs
- ✅ **Gamma Adjustment**: Real-time gamma correction slider in expanded image modal
- ✅ **Code Cleanup**: Removed unnecessary debug print statements

## Support

For issues or questions, refer to the code comments in each component file or check the implementation details in:
- `components/report_generation.py` - Report generation logic
- `components/image_viewer.py` - Image viewing and filtering
- `components/confusion_matrix.py` - Matrix generation and cell clicking
- `components/analytics.py` - Analytics calculations
- `components/threshold_tweaker.py` - Threshold adjustment and optimization
- `components/cell_details.py` - Cell detail filtering and display
