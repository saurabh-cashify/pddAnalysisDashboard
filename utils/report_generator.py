"""
Report Generation Utility
Integrates functionality from raw_data_analysis.py to generate analysis CSV
"""

import requests
import pandas as pd
import time
import json
import os
import numpy as np

# Set matplotlib to non-GUI backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server-side plotting
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from .threshold_handler import (
    load_threshold_config,
    get_category_from_score,
    get_severity_order_from_thresholds,
    normalize_category_for_confusion_matrix,
    get_category_order_from_threshold,
    is_least_severe_category
)


class ReportGenerator:
    """Generate analysis reports from raw data CSV"""
    
    def __init__(
        self,
        api_key: str,
        query_id: int,
        base_url: str,
        question_name: str,
        back_key: str = "backmerged",
        front_key: str = "whiterotatedmerged",
        mode: str = "qc_automation",
        threshold_path: Optional[str] = None
    ):
        """
        Initialize Report Generator
        
        Args:
            api_key: Redash API key
            query_id: Redash query ID
            base_url: Redash base URL
            question_name: Question name (e.g., 'physicalConditionScratch')
            back_key: Key for back side images
            front_key: Key for front side images
            mode: Mode for query
            threshold_path: Optional path to threshold.json file (if None, uses default)
        """
        self.api_key = api_key
        self.query_id = query_id
        self.base_url = base_url
        self.question_name = question_name
        self.back_key = back_key
        self.front_key = front_key
        self.mode = mode
        self.threshold_config = load_threshold_config(threshold_path)
    
    def load_raw_data_csv(self, csv_path: str, source: str = "Cscanpro-Line2") -> pd.DataFrame:
        """
        Load raw data CSV with multiple encoding/delimiter attempts
        
        Args:
            csv_path: Path to raw data CSV
            source: Source type - "Cscanpro-Line2" or "Cscanpro-Line3"
            
        Returns:
            DataFrame with raw data
        """
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
        delimiters = ['\t', ',', ';']
        raw_df = None
        
        for enc in encodings:
            for delim in delimiters:
                try:
                    raw_df = pd.read_csv(csv_path, encoding=enc, sep=delim)
                    if len(raw_df.columns) > 1:
                        print(f"✅ Loaded CSV with encoding: {enc}, delimiter: '{delim}'")
                        break
                except Exception:
                    continue
            if raw_df is not None and len(raw_df.columns) > 1:
                break
        
        if raw_df is None:
            # Last attempt with auto-detection
            for enc in encodings:
                try:
                    raw_df = pd.read_csv(csv_path, encoding=enc, sep=None, engine='python')
                    print(f"✅ Loaded CSV with encoding: {enc}, auto-detected delimiter")
                    break
                except Exception:
                    continue
        
        if raw_df is None:
            raise ValueError(f"Could not load {csv_path} with any encoding/delimiter")
        
        # Validate columns based on source
        if source == "Cscanpro-Line3":
            required_cols = ['line1/2_txn_id', 'line3_txn_id', 'tester_answer', 'line1/2_answer', 'line3_answer', 'created_date']
            missing_cols = [col for col in required_cols if col not in raw_df.columns]
            if missing_cols:
                raise KeyError(f"Missing columns for Line3 CSV: {missing_cols}. Available: {list(raw_df.columns)}")
        else:
            # Line2 validation
            if 'pdd_txn_id' not in raw_df.columns:
                raise KeyError(f"Column 'pdd_txn_id' not found. Available: {list(raw_df.columns)}")
        
        return raw_df
    
    def execute_redash_query(self, pdd_txn_ids: List[str]) -> pd.DataFrame:
        """
        Execute Redash query and get results
        
        Args:
            pdd_txn_ids: List of transaction IDs
            
        Returns:
            DataFrame with query results
        """
        # Format as comma-separated string with single quotes
        pdd_txn_ids_str = "'" + "','".join(pdd_txn_ids) + "'"
        
        params = {
            "question_name": self.question_name,
            "pdd_txn_ids": pdd_txn_ids_str,
            "mode": self.mode,
            "back_key": self.back_key,
            "front_key": self.front_key,
        }
        
        # Trigger query execution
        print("🔄 Running query on Redash...")
        run_url = f"{self.base_url}/api/queries/{self.query_id}/results"
        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        
        run_response = requests.post(run_url, headers=headers, json={"parameters": params})
        if run_response.status_code != 200:
            raise Exception(f"Failed to trigger query: {run_response.text}")
        
        try:
            run_response = run_response.json()
        except Exception as e:
            raise Exception(f"❌ Failed to parse JSON: {e}\nResponse: {run_response.text}")
        
        # Handle cached results or job polling
        if "query_result" in run_response:
            print("✅ Query result available immediately (cached).")
            query_result = run_response["query_result"]
            data_rows = query_result["data"]["rows"]
            columns = query_result["data"]["columns"]
        else:
            # Poll for job completion
            job = run_response.get("job")
            if not job:
                raise Exception(f"❌ Could not start job. Response: {run_response}")
            
            job_id = job["id"]
            print(f"⏳ Query started. Job ID: {job_id}")
            
            status_url = f"{self.base_url}/api/jobs/{job_id}"
            while True:
                status_resp = requests.get(status_url, headers=headers)
                status = status_resp.json()
                
                state = status["job"]["status"]
                if state == 3:  # success
                    print("✅ Query completed.")
                    query_result_id = status["job"]["query_result_id"]
                    break
                elif state == 4:  # failed
                    raise Exception(f"❌ Query failed. Details: {status}")
                else:
                    print("⏳ Still running... waiting 3s")
                    time.sleep(3)
            
            # Fetch results
            results_url = f"{self.base_url}/api/query_results/{query_result_id}.json?api_key={self.api_key}"
            print("📥 Fetching latest results...")
            results_resp = requests.get(results_url)
            results = results_resp.json()
            
            if "query_result" not in results:
                raise Exception(f"❌ Unexpected result structure: {results}")
            
            query_result = results["query_result"]
            data_rows = query_result["data"]["rows"]
            columns = query_result["data"]["columns"]
        
        # Create DataFrame
        df = pd.DataFrame(data_rows)
        column_order = [col["name"] for col in columns]
        df = df[column_order]
        
        print(f"📊 Redash query returned {len(df)} rows")
        return df
    
    def join_with_raw_data(self, redash_df: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Join Redash results with raw data CSV
        
        Args:
            redash_df: DataFrame from Redash query
            raw_df: DataFrame from raw data CSV
            
        Returns:
            Joined DataFrame
        """
        columns_to_add = ['quote_date', 'qc_answer', 'auditor_answer', 'cscan_answer']
        missing_columns = [col for col in columns_to_add if col not in raw_df.columns]
        if missing_columns:
            raise KeyError(f"Missing columns in input CSV: {missing_columns}")
        
        input_join_data = raw_df[['pdd_txn_id'] + columns_to_add].copy()
        joined_df = redash_df.merge(input_join_data, on='pdd_txn_id', how='left')
        
        print(f"✅ Join completed. Final dataset: {len(joined_df)} rows")
        return joined_df
    
    def create_final_answer_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create final_answer column
        Uses auditor_answer if not blank, otherwise uses qc_answer
        """
        def is_blank(value):
            if pd.isna(value):
                return True
            if isinstance(value, str):
                return not value.strip()
            return False
        
        df['final_answer'] = df.apply(
            lambda row: row['auditor_answer'] if not is_blank(row.get('auditor_answer')) 
                       else row.get('qc_answer', None),  # Use qc_answer when auditor_answer is missing
            axis=1
        )
        
        # Place final_answer after cscan_answer
        if 'cscan_answer' in df.columns:
            cols = list(df.columns)
            cscan_idx = cols.index('cscan_answer')
            cols.remove('final_answer')
            cols.insert(cscan_idx + 1, 'final_answer')
            df = df[cols]
        
        return df
    
    def create_contributing_sides(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create contributing_sides column based on original scores and thresholds
        Shows which sides contributed to the cscan_answer
        
        Args:
            df: DataFrame with original *_score columns and cscan_answer
            
        Returns:
            DataFrame with contributing_sides column added after cscan_answer
        """
        if 'cscan_answer' not in df.columns:
            print("⚠️  cscan_answer column not found, skipping contributing_sides")
            return df
        
        if self.question_name not in self.threshold_config:
            print(f"⚠️  Question '{self.question_name}' not in threshold config")
            return df
        
        question_thresholds = self.threshold_config[self.question_name]
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        contributing_sides_list = []
        
        for idx, row in df.iterrows():
            cscan_answer = row['cscan_answer']
            
            # If no cscan_answer, no contributing sides
            if pd.isna(cscan_answer) or (isinstance(cscan_answer, str) and not cscan_answer.strip()):
                contributing_sides_list.append(None)
                continue
            
            side_categories = []  # List of tuples: (side, category, score)
            
            for side in sides:
                score_col = f"{side}_score"
                if score_col not in df.columns:
                    continue
                
                score = row[score_col]
                if pd.isna(score):
                    continue
                
                if side not in question_thresholds:
                    continue
                
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(score, side_thresholds)
                
                if category:
                    side_categories.append((side, category, score))
            
            if not side_categories:
                contributing_sides_list.append(None)
            else:
                # Check if cscan_answer is the least severe category
                # If so, don't populate contributing_sides
                if is_least_severe_category(cscan_answer, self.question_name, self.threshold_config):
                    contributing_sides_list.append(None)
                else:
                    # Find all sides that match the cscan_answer
                    contributing_sides = [side for side, cat, _ in side_categories if cat == cscan_answer]
                    
                    contributing_sides_list.append(', '.join(contributing_sides) if contributing_sides else None)
        
        # Add contributing_sides column after cscan_answer
        result_df = df.copy()
        if 'cscan_answer' in result_df.columns:
            cols = list(result_df.columns)
            cscan_idx = cols.index('cscan_answer')
            cols.insert(cscan_idx + 1, 'contributing_sides')
            result_df['contributing_sides'] = contributing_sides_list
            result_df = result_df[cols]
        else:
            result_df['contributing_sides'] = contributing_sides_list
        
        return result_df
    
    def calculate_accuracy(self, df: pd.DataFrame, predicted_col: str, accuracy_col: str) -> pd.DataFrame:
        """
        Calculate accuracy percentage grouped by quote_date
        
        Args:
            df: DataFrame
            predicted_col: Column name for predictions
            accuracy_col: Column name to store accuracy (e.g., 'acc%')
            
        Returns:
            DataFrame with accuracy column
        """
        if 'quote_date' not in df.columns or predicted_col not in df.columns:
            return df
        
        df[accuracy_col] = None
        
        for date, group in df.groupby('quote_date'):
            if len(group) == 0:
                continue
            
            matches = 0
            total = 0
            for _, row in group.iterrows():
                predicted = row.get(predicted_col)
                final = row.get('final_answer')
                
                if pd.isna(predicted) or pd.isna(final):
                    continue
                
                total += 1
                if str(predicted).strip().lower() == str(final).strip().lower():
                    matches += 1
            
            if total > 0:
                accuracy = (matches / total) * 100
                first_idx = group.index[0]
                df.at[first_idx, accuracy_col] = round(accuracy, 2)
        
        return df
    
    def create_contributing_sides_line3(self, df: pd.DataFrame, cscan_col: str, output_col: str, prefix: str = 'line2_') -> pd.DataFrame:
        """
        Create contributing_sides column for Line3 with prefix support
        Similar to create_contributing_sides but works with prefixed columns
        """
        if cscan_col not in df.columns:
            print(f"⚠️  {cscan_col} column not found, skipping {output_col}")
            return df
        
        if self.question_name not in self.threshold_config:
            print(f"⚠️  Question '{self.question_name}' not in threshold config")
            return df
        
        question_thresholds = self.threshold_config[self.question_name]
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        result_df = df.copy()
        result_df[output_col] = None
        
        for idx, row in df.iterrows():
            cscan_answer = row.get(cscan_col)
            
            if pd.isna(cscan_answer) or (isinstance(cscan_answer, str) and not cscan_answer.strip()):
                continue
            
            side_categories = []
            
            for side in sides:
                score_col = f'{prefix}{side}_score' if prefix else f'{side}_score'
                if score_col not in df.columns:
                    continue
                
                score = row.get(score_col)
                if pd.isna(score):
                    continue
                
                if side not in question_thresholds:
                    continue
                
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(score, side_thresholds)
                side_categories.append((side, category, score))
            
            if not side_categories:
                continue
            
            # Check if cscan_answer is least severe
            if is_least_severe_category(cscan_answer, self.question_name, self.threshold_config):
                # If least severe, don't populate contributing_sides (same as original)
                contributing_sides = []
            else:
                # Find all sides that match the cscan_answer (same logic as original)
                contributing_sides = [side for side, cat, _ in side_categories if cat == cscan_answer]
            
            result_df.at[idx, output_col] = ', '.join(contributing_sides) if contributing_sides else ''
        
        # Place column after cscan_col
        cols = list(result_df.columns)
        if cscan_col in cols:
            cscan_idx = cols.index(cscan_col)
            cols.remove(output_col)
            cols.insert(cscan_idx + 1, output_col)
            result_df = result_df[cols]
        
        return result_df
    
    def join_with_eval_results(self, df: pd.DataFrame, eval_folder: str) -> pd.DataFrame:
        """
        Join DataFrame with eval CSV results
        
        Args:
            df: Main DataFrame
            eval_folder: Path to folder containing eval CSV files
            
        Returns:
            DataFrame with eval results joined
        """
        if not os.path.exists(eval_folder):
            print(f"⚠️  Eval folder not found: {eval_folder}")
            return df
        
        eval_files = [f for f in os.listdir(eval_folder) if f.endswith('.csv')]
        if not eval_files:
            print(f"⚠️  No CSV files found in eval folder")
            return df
        
        print(f"📊 Found {len(eval_files)} eval CSV files")
        
        # Pre-process: Remove rows with missing UUIDs from eval CSVs
        print(f"🔍 Pre-processing eval CSVs - removing rows with missing UUIDs...")
        
        new_columns = {}
        processed_uuids = set()
        side_match_counts = {}
        
        for eval_file in eval_files:
            eval_path = os.path.join(eval_folder, eval_file)
            print(f"📖 Processing: {eval_file}")
            
            try:
                eval_df = pd.read_csv(eval_path)
                required_cols = ['image_uuid', 'score', 'result_image_url']
                missing_cols = [col for col in required_cols if col not in eval_df.columns]
                if missing_cols:
                    print(f"⚠️  Missing columns: {missing_cols}")
                    continue
                
                initial_count = len(eval_df)
                
                # Remove rows with missing/null image_uuid
                eval_df = eval_df[eval_df['image_uuid'].notna()]
                eval_df = eval_df[eval_df['image_uuid'].astype(str).str.strip() != '']
                
                # Additional filtering: ensure UUID JSON is valid
                def has_valid_uuid(uuid_str):
                    try:
                        uuid_json = json.loads(uuid_str)
                        return isinstance(uuid_json, dict) and len(uuid_json) > 0
                    except:
                        return False
                
                eval_df = eval_df[eval_df['image_uuid'].apply(has_valid_uuid)]
                filtered_count = initial_count - len(eval_df)
                if filtered_count > 0:
                    print(f"   ⚠️  Removed {filtered_count} rows with missing/invalid UUIDs from {eval_file}")
                
                if 'question' in eval_df.columns:
                    eval_df = eval_df[eval_df['question'] == self.question_name]
                
                for _, row in eval_df.iterrows():
                    try:
                        image_uuid_json = json.loads(row['image_uuid'])
                        side = None
                        uuid_value = None
                        
                        if self.back_key in image_uuid_json:
                            uuid_value = image_uuid_json[self.back_key]
                            side = "back"
                        elif self.front_key in image_uuid_json:
                            uuid_value = image_uuid_json[self.front_key]
                            side = "front"
                        else:
                            if len(image_uuid_json) == 1:
                                key, uuid_value = list(image_uuid_json.items())[0]
                                key_lower = key.lower()
                                if key_lower in ['top', 'bottom', 'left', 'right']:
                                    side = key_lower
                        
                        if side and uuid_value:
                            unique_key = f"{side}_{uuid_value}"
                            if unique_key in processed_uuids:
                                continue
                            
                            processed_uuids.add(unique_key)
                            uuid_column = f"{side}_uuid"
                            
                            if uuid_column not in df.columns:
                                continue
                            
                            matching_rows = df[df[uuid_column] == uuid_value]
                            if matching_rows.empty:
                                continue
                            
                            score_col = f"new_{side}_score"
                            url_col = f"new_{side}_result_image_url"
                            
                            if score_col not in new_columns:
                                new_columns[score_col] = {}
                            if url_col not in new_columns:
                                new_columns[url_col] = {}
                            
                            for idx in matching_rows.index:
                                new_columns[score_col][idx] = row['score']
                                new_columns[url_col][idx] = row['result_image_url']
                            
                            if side not in side_match_counts:
                                side_match_counts[side] = 0
                            side_match_counts[side] += len(matching_rows)
                    except Exception as e:
                        print(f"⚠️  Error processing row: {e}")
                        continue
            except Exception as e:
                print(f"⚠️  Error reading {eval_file}: {e}")
                continue
        
        # Add new columns
        result_df = df.copy()
        for col_name, values in new_columns.items():
            result_df[col_name] = None
            for idx, value in values.items():
                result_df.at[idx, col_name] = value
        
        print(f"✅ Added {len(new_columns)} eval columns")
        
        # Identify which sides have eval data (from side_match_counts or new_columns)
        sides_with_eval_data = set(side_match_counts.keys())
        
        # Alternative: extract from new_columns keys if side_match_counts is empty
        if not sides_with_eval_data:
            for col_name in new_columns.keys():
                if col_name.startswith('new_') and col_name.endswith('_score'):
                    side = col_name.replace('new_', '').replace('_score', '')
                    if side in ['top', 'bottom', 'left', 'right', 'back', 'front']:
                        sides_with_eval_data.add(side)
        
        print(f"📊 Sides with eval data: {sorted(sides_with_eval_data)}")
        
        # For sides without eval data, copy from deployed values
        all_sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        sides_without_eval = [side for side in all_sides if side not in sides_with_eval_data]
        
        if sides_without_eval:
            print(f"📋 Sides without eval data (will use deployed values): {sorted(sides_without_eval)}")
            for side in sides_without_eval:
                deployed_score_col = f"{side}_score"
                deployed_url_col = f"{side}_result_url"
                new_score_col = f"new_{side}_score"
                new_url_col = f"new_{side}_result_image_url"
                
                # Check if deployed columns exist
                if deployed_score_col in result_df.columns:
                    result_df[new_score_col] = result_df[deployed_score_col]
                    print(f"   ✓ Copied {deployed_score_col} → {new_score_col}")
                else:
                    print(f"   ⚠️  {deployed_score_col} not found, skipping")
                
                if deployed_url_col in result_df.columns:
                    result_df[new_url_col] = result_df[deployed_url_col]
                    print(f"   ✓ Copied {deployed_url_col} → {new_url_col}")
                else:
                    print(f"   ⚠️  {deployed_url_col} not found, skipping")
        
        # Post-processing: Remove rows where required UUIDs are missing/empty
        # Identify which sides have new scores (these are the sides we need UUIDs for)
        sides_with_new_scores = []
        for side in ['top', 'bottom', 'left', 'right', 'back', 'front']:
            score_col = f"new_{side}_score"
            if score_col in result_df.columns and result_df[score_col].notna().any():
                sides_with_new_scores.append(side)
        
        if sides_with_new_scores:
            initial_count = len(result_df)
            print(f"\n🔍 Post-processing: Checking for missing UUIDs in sides: {sides_with_new_scores}")
            
            # Filter: Keep rows where ALL required UUIDs are present and not empty
            for side in sides_with_new_scores:
                uuid_col = f"{side}_uuid"
                if uuid_col in result_df.columns:
                    # Remove rows where this UUID is missing or empty
                    result_df = result_df[result_df[uuid_col].notna()]
                    result_df = result_df[result_df[uuid_col].astype(str).str.strip() != '']
            
            removed_count = initial_count - len(result_df)
            if removed_count > 0:
                print(f"   ⚠️  Removed {removed_count} rows with missing/empty UUIDs for eval sides")
                print(f"   ✓ Remaining rows: {len(result_df)}")
        
        return result_df
    
    def create_new_cscan_answer(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new_cscan_answer and new_contributing_sides columns based on thresholds
        
        Args:
            df: DataFrame with new_*_score columns
            
        Returns:
            DataFrame with new_cscan_answer and new_contributing_sides columns
        """
        if self.question_name not in self.threshold_config:
            print(f"⚠️  Question '{self.question_name}' not in threshold config")
            return df
        
        question_thresholds = self.threshold_config[self.question_name]
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        new_answers = []
        new_contributing_sides_list = []
        
        for idx, row in df.iterrows():
            side_categories = []  # List of tuples: (side, category, score)
            
            for side in sides:
                score_col = f"new_{side}_score"
                if score_col not in df.columns:
                    continue
                
                score = row[score_col]
                if pd.isna(score):
                    continue
                
                if side not in question_thresholds:
                    continue
                
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(score, side_thresholds)
                
                if category:
                    side_categories.append((side, category, score))
            
            # Determine final answer based on severity priority
            if not side_categories:
                new_answers.append(None)
                new_contributing_sides_list.append(None)
            else:
                # Extract all unique categories from all sides
                all_categories = [cat for _, cat, _ in side_categories]
                
                # Priority-based selection: check categories in severity order (highest first)
                final_answer = None
                for category in severity_order:
                    if category in all_categories:
                        final_answer = category
                        break
                
                # Fallback: if no match found, use first category (shouldn't happen)
                if final_answer is None:
                    final_answer = all_categories[0] if all_categories else None
                
                # Check if final_answer is the least severe category
                # If so, don't populate contributing_sides
                if is_least_severe_category(final_answer, self.question_name, self.threshold_config):
                    new_answers.append(final_answer)
                    new_contributing_sides_list.append(None)
                else:
                    # Find all sides that contributed to this final answer
                    contributing_sides = [side for side, cat, _ in side_categories if cat == final_answer]
                    
                    new_answers.append(final_answer)
                    new_contributing_sides_list.append(', '.join(contributing_sides) if contributing_sides else None)
        
        # Add new_cscan_answer and new_contributing_sides columns after final_answer
        result_df = df.copy()
        if 'final_answer' in result_df.columns:
            # Find position of final_answer
            cols = list(result_df.columns)
            final_idx = cols.index('final_answer')
            # Insert new_cscan_answer after final_answer
            cols.insert(final_idx + 1, 'new_cscan_answer')
            # Insert new_contributing_sides after new_cscan_answer
            cols.insert(final_idx + 2, 'new_contributing_sides')
            result_df['new_cscan_answer'] = new_answers
            result_df['new_contributing_sides'] = new_contributing_sides_list
            result_df = result_df[cols]
        else:
            # If final_answer not found, just append
            result_df['new_cscan_answer'] = new_answers
            result_df['new_contributing_sides'] = new_contributing_sides_list
        
        return result_df
    
    def save_uuid_json_files(self, df: pd.DataFrame, output_folder: str):
        """Save UUID JSON files for each side"""
        os.makedirs(output_folder, exist_ok=True)
        
        uuid_columns = {
            'top_uuid': 'top_uuid.json',
            'bottom_uuid': 'bottom_uuid.json',
            'right_uuid': 'right_uuid.json',
            'left_uuid': 'left_uuid.json',
            'back_uuid': 'back_uuid.json',
            'front_uuid': 'front_uuid.json'
        }
        
        for uuid_column, filename in uuid_columns.items():
            if uuid_column in df.columns:
                uuids = df[uuid_column].dropna().tolist()
                uuid_list = [{"image_uuid": uuid} for uuid in uuids if uuid and str(uuid).strip()]
                
                filepath = os.path.join(output_folder, filename)
                with open(filepath, 'w') as f:
                    json.dump(uuid_list, f, indent=2)
                
                print(f"✅ Saved {len(uuid_list)} UUIDs to {filepath}")
    
    def save_uuid_json_files_line3(self, df: pd.DataFrame, output_folder: str):
        """Save UUID JSON files for Line3 - both line2_* prefixed and regular"""
        os.makedirs(output_folder, exist_ok=True)
        
        # Regular UUID files (from line3 results)
        uuid_columns = {
            'top_uuid': 'top_uuid.json',
            'bottom_uuid': 'bottom_uuid.json',
            'right_uuid': 'right_uuid.json',
            'left_uuid': 'left_uuid.json',
            'back_uuid': 'back_uuid.json',
            'front_uuid': 'front_uuid.json'
        }
        
        for uuid_column, filename in uuid_columns.items():
            if uuid_column in df.columns:
                uuids = df[uuid_column].dropna().tolist()
                uuid_list = [{"image_uuid": uuid} for uuid in uuids if uuid and str(uuid).strip()]
                
                filepath = os.path.join(output_folder, filename)
                with open(filepath, 'w') as f:
                    json.dump(uuid_list, f, indent=2)
                
                print(f"✅ Saved {len(uuid_list)} UUIDs to {filepath}")
        
        # Line2 UUID files (with line2_ prefix)
        line2_uuid_columns = {
            'line2_top_uuid': 'line2_top_uuid.json',
            'line2_bottom_uuid': 'line2_bottom_uuid.json',
            'line2_right_uuid': 'line2_right_uuid.json',
            'line2_left_uuid': 'line2_left_uuid.json',
            'line2_back_uuid': 'line2_back_uuid.json',
            'line2_front_uuid': 'line2_front_uuid.json'
        }
        
        for uuid_column, filename in line2_uuid_columns.items():
            if uuid_column in df.columns:
                uuids = df[uuid_column].dropna().tolist()
                uuid_list = [{"image_uuid": uuid} for uuid in uuids if uuid and str(uuid).strip()]
                
                filepath = os.path.join(output_folder, filename)
                with open(filepath, 'w') as f:
                    json.dump(uuid_list, f, indent=2)
                
                print(f"✅ Saved {len(uuid_list)} UUIDs to {filepath}")
    
    def reorder_columns(self, df: pd.DataFrame, include_new_columns: bool = False) -> pd.DataFrame:
        """
        Reorder columns according to specified order
        
        Args:
            df: DataFrame to reorder
            include_new_columns: If True, includes new_* columns (after eval)
            
        Returns:
            DataFrame with reordered columns
        """
        # Base column order (initial CSV)
        base_order = [
            'pdd_txn_id',
            'image_timestamp',
            'top_uuid', 'bottom_uuid', 'right_uuid', 'left_uuid', 'back_uuid', 'front_uuid',
            'top_request_body', 'bottom_request_body', 'right_request_body', 
            'left_request_body', 'back_request_body', 'front_request_body',
            'top_image_url', 'bottom_image_url', 'right_image_url', 
            'left_image_url', 'back_image_url', 'front_image_url',
            'top_result_url', 'bottom_result_url', 'right_result_url', 
            'left_result_url', 'back_result_url', 'front_result_url',
            'top_score', 'bottom_score', 'right_score', 
            'left_score', 'back_score', 'front_score',
            'quote_date', 'qc_answer', 'auditor_answer', 'cscan_answer',
            'final_answer', 'contributing_sides', 'acc%'
        ]
        
        # Additional columns for after eval
        if include_new_columns:
            new_columns = [
                'new_cscan_answer',
                'new_top_score', 'new_bottom_score', 'new_right_score', 
                'new_left_score', 'new_back_score', 'new_front_score',
                'new_top_result_image_url', 'new_bottom_result_image_url', 
                'new_right_result_image_url', 'new_left_result_image_url', 
                'new_back_result_image_url', 'new_front_result_image_url',
                'new_contributing_sides', 'new_acc%'
            ]
            # Insert new columns after acc%
            base_order.extend(new_columns)
        
        # Get all columns that exist in df
        existing_ordered = [col for col in base_order if col in df.columns]
        
        # Add any extra columns that aren't in our predefined order (shouldn't happen, but safety)
        extra_cols = [col for col in df.columns if col not in existing_ordered]
        
        final_order = existing_ordered + extra_cols
        
        return df[final_order]
    
    def _get_date_range_title(self, df: pd.DataFrame) -> str:
        """
        Extract date range from quote_date column and format as title.
        Returns "Confusion Matrix: dd/mm/yyyy" or "Confusion Matrix: dd/mm/yyyy - dd/mm/yyyy" if multiple dates.
        """
        if 'quote_date' not in df.columns:
            return "Confusion Matrix"
        
        try:
            # Extract valid dates
            date_series = df['quote_date'].dropna()
            if len(date_series) == 0:
                return "Confusion Matrix"
            
            # Try to parse dates - handle various formats
            dates = []
            for date_val in date_series:
                try:
                    # Try pandas to_datetime which handles multiple formats
                    parsed_date = pd.to_datetime(date_val)
                    dates.append(parsed_date)
                except (ValueError, TypeError):
                    continue
            
            if len(dates) == 0:
                return "Confusion Matrix"
            
            # Get min and max dates
            min_date = min(dates)
            max_date = max(dates)
            
            # Format as dd/mm/yyyy
            date_format = "%d/%m/%Y"
            
            if min_date == max_date:
                # Single date
                return f"Confusion Matrix: {min_date.strftime(date_format)}"
            else:
                # Date range
                return f"Confusion Matrix: {min_date.strftime(date_format)} - {max_date.strftime(date_format)}"
        
        except Exception as e:
            print(f"⚠️  Error extracting date range for confusion matrix title: {e}")
            return "Confusion Matrix"
    
    def create_confusion_matrices(self, df: pd.DataFrame, output_folder: str):
        """Create confusion matrix PNG files"""
        # Get date-based title
        date_title = self._get_date_range_title(df)
        
        # Create confusion matrix for cscan_answer vs final_answer
        if 'cscan_answer' in df.columns and 'final_answer' in df.columns:
            confusion_matrix_path = os.path.join(output_folder, "confusion_matrix_acc.png")
            self._create_confusion_matrix(
                df=df,
                predicted_col='cscan_answer',
                actual_col='final_answer',
                output_path=confusion_matrix_path,
                title=date_title
            )
        
        # Create comparison confusion matrix if new_cscan_answer exists
        if ('cscan_answer' in df.columns and 
            'new_cscan_answer' in df.columns and 
            'final_answer' in df.columns):
            comparison_matrix_path = os.path.join(output_folder, "confusion_matrix_comparison.png")
            self._create_comparison_confusion_matrix(
                df=df,
                predicted_col_before='cscan_answer',
                predicted_col_after='new_cscan_answer',
                actual_col='final_answer',
                output_path=comparison_matrix_path,
                date_title=date_title
            )
    
    def _create_confusion_matrix(
        self, df: pd.DataFrame, predicted_col: str, actual_col: str,
        output_path: str, title: str
    ):
        """Create and save a confusion matrix visualization"""
        valid_df = df[[predicted_col, actual_col]].dropna()
        
        if len(valid_df) == 0:
            print(f"⚠️  No valid data for confusion matrix")
            return
        
        # Normalize values
        predicted_values = valid_df[predicted_col].apply(
            lambda x: normalize_category_for_confusion_matrix(x, self.question_name)
        )
        actual_values = valid_df[actual_col].apply(
            lambda x: normalize_category_for_confusion_matrix(x, self.question_name)
        )
        
        # Get category order
        data_categories = set(predicted_values.unique()) | set(actual_values.unique())
        threshold_order = get_category_order_from_threshold(self.question_name, self.threshold_config)
        
        if threshold_order:
            all_categories = [cat for cat in threshold_order if cat in data_categories]
            missing_categories = sorted(data_categories - set(all_categories))
            all_categories.extend(missing_categories)
        else:
            all_categories = sorted(data_categories)
        
        if len(all_categories) == 0:
            return
        
        # Create confusion matrix
        cm = pd.crosstab(actual_values, predicted_values, margins=False)
        
        # Ensure all categories are present
        for cat in all_categories:
            if cat not in cm.index:
                cm.loc[cat] = 0
            if cat not in cm.columns:
                cm[cat] = 0
        
        cm = cm.reindex(index=all_categories, columns=all_categories, fill_value=0)
        
        # Create plot
        plt.figure(figsize=(max(8, len(all_categories) * 0.8), max(6, len(all_categories) * 0.7)))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': 'Count'},
                    linewidths=0.5, linecolor='gray')
        
        plt.xlabel(f'Predicted ({predicted_col})', fontsize=12, fontweight='bold')
        plt.ylabel(f'Actual ({actual_col})', fontsize=12, fontweight='bold')
        plt.title(f"{title}\nQuestion: {self.question_name}", fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Confusion matrix saved: {output_path}")
    
    def _create_comparison_confusion_matrix(
        self, df: pd.DataFrame, predicted_col_before: str,
        predicted_col_after: str, actual_col: str, output_path: str, date_title: str = None
    ):
        """Create side-by-side comparison confusion matrix"""
        def get_cm(predicted_col, actual_col):
            valid_df = df[[predicted_col, actual_col]].dropna()
            if len(valid_df) == 0:
                return None, None, 0
            
            predicted_values = valid_df[predicted_col].apply(
                lambda x: normalize_category_for_confusion_matrix(x, self.question_name)
            )
            actual_values = valid_df[actual_col].apply(
                lambda x: normalize_category_for_confusion_matrix(x, self.question_name)
            )
            
            data_categories = set(predicted_values.unique()) | set(actual_values.unique())
            threshold_order = get_category_order_from_threshold(self.question_name, self.threshold_config)
            
            if threshold_order:
                all_categories = [cat for cat in threshold_order if cat in data_categories]
                missing_categories = sorted(data_categories - set(all_categories))
                all_categories.extend(missing_categories)
            else:
                all_categories = sorted(data_categories)
            
            if len(all_categories) == 0:
                return None, None, 0
            
            cm = pd.crosstab(actual_values, predicted_values, margins=False)
            
            for cat in all_categories:
                if cat not in cm.index:
                    cm.loc[cat] = 0
                if cat not in cm.columns:
                    cm[cat] = 0
            
            cm = cm.reindex(index=all_categories, columns=all_categories, fill_value=0)
            return cm, all_categories, len(valid_df)
        
        cm_before, categories_before, count_before = get_cm(predicted_col_before, actual_col)
        cm_after, categories_after, count_after = get_cm(predicted_col_after, actual_col)
        
        if cm_before is None or cm_after is None:
            return
        
        # Use union of categories
        data_categories = set(categories_before) | set(categories_after)
        threshold_order = get_category_order_from_threshold(self.question_name, self.threshold_config)
        
        if threshold_order:
            all_categories = [cat for cat in threshold_order if cat in data_categories]
            missing_categories = sorted(data_categories - set(all_categories))
            all_categories.extend(missing_categories)
        else:
            all_categories = sorted(data_categories)
        
        # Ensure both matrices have same categories
        for cat in all_categories:
            if cat not in cm_before.index:
                cm_before.loc[cat] = 0
            if cat not in cm_before.columns:
                cm_before[cat] = 0
            if cat not in cm_after.index:
                cm_after.loc[cat] = 0
            if cat not in cm_after.columns:
                cm_after[cat] = 0
        
        cm_before = cm_before.reindex(index=all_categories, columns=all_categories, fill_value=0)
        cm_after = cm_after.reindex(index=all_categories, columns=all_categories, fill_value=0)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(max(16, len(all_categories) * 1.6), max(6, len(all_categories) * 0.7)))
        
        vmax = max(cm_before.values.max(), cm_after.values.max())
        
        sns.heatmap(cm_before, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': 'Count'},
                    linewidths=0.5, linecolor='gray', ax=ax1, vmin=0, vmax=vmax)
        ax1.set_xlabel(f'Predicted ({predicted_col_before})', fontsize=11, fontweight='bold')
        ax1.set_ylabel(f'Actual ({actual_col})', fontsize=11, fontweight='bold')
        ax1.set_title('Before (cscan_answer)', fontsize=12, fontweight='bold', pad=10)
        
        sns.heatmap(cm_after, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': 'Count'},
                    linewidths=0.5, linecolor='gray', ax=ax2, vmin=0, vmax=vmax)
        ax2.set_xlabel(f'Predicted ({predicted_col_after})', fontsize=11, fontweight='bold')
        ax2.set_ylabel(f'Actual ({actual_col})', fontsize=11, fontweight='bold')
        ax2.set_title('After (new_cscan_answer)', fontsize=12, fontweight='bold', pad=10)
        
        # Use date-based title if provided, otherwise use default
        if date_title is None:
            date_title = self._get_date_range_title(df)
        fig.suptitle(f"{date_title} - Comparison\nQuestion: {self.question_name}", 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Comparison confusion matrix saved: {output_path}")
    
    def process_line3_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process Line3 data: extract both line1/2_txn_id and line3_txn_id,
        run separate queries, and merge results with appropriate prefixes.
        
        Args:
            raw_df: Raw DataFrame with Line3 structure
            
        Returns:
            DataFrame with both line2_* and regular columns merged
        """
        print("\n🔄 Processing Line3 data (dual queries)...")
        
        # Filter out rows where any of line1/2_answer, line3_answer, or tester_answer is "Not Checked"
        initial_count = len(raw_df)
        answer_columns = ['line1/2_answer', 'line3_answer', 'tester_answer']
        
        # Check which columns exist
        existing_answer_cols = [col for col in answer_columns if col in raw_df.columns]
        
        if existing_answer_cols:
            # Filter out rows where any of these columns has "Not Checked"
            mask = ~raw_df[existing_answer_cols].apply(
                lambda row: row.astype(str).str.strip().str.lower().eq('not checked').any(),
                axis=1
            )
            raw_df = raw_df[mask].copy()
            filtered_count = initial_count - len(raw_df)
            
            if filtered_count > 0:
                print(f"🗑️  Filtered out {filtered_count} rows with 'Not Checked' in answer columns")
                print(f"   Remaining rows: {len(raw_df)}")
            else:
                print(f"   ✓ No rows with 'Not Checked' found")
        
        # Step 1: Extract line1/2_txn_id and run query
        print("\n📋 Step 1: Processing line1/2_txn_id...")
        line2_txn_ids = raw_df['line1/2_txn_id'].dropna().unique().tolist()
        print(f"✅ Found {len(line2_txn_ids)} unique line1/2_txn_id values")
        
        if len(line2_txn_ids) > 0:
            # Execute query for line2
            BATCH_SIZE = 3000
            if len(line2_txn_ids) > BATCH_SIZE:
                print(f"⚠️  Found {len(line2_txn_ids)} IDs (exceeds limit of {BATCH_SIZE})")
                print(f"📦 Splitting into batches...")
                batches = []
                for i in range(0, len(line2_txn_ids), BATCH_SIZE):
                    batches.append(line2_txn_ids[i:i + BATCH_SIZE])
                
                all_results = []
                for batch_num, batch in enumerate(batches, 1):
                    print(f"🔄 Processing line2 batch {batch_num}/{len(batches)}...")
                    batch_df = self.execute_redash_query(batch)
                    all_results.append(batch_df)
                
                line2_redash_df = pd.concat(all_results, ignore_index=True)
            else:
                line2_redash_df = self.execute_redash_query(line2_txn_ids)
            
            # Add line2_ prefix to all columns except pdd_txn_id (which we'll rename)
            line2_redash_df = line2_redash_df.rename(columns={
                'pdd_txn_id': 'line2_pdd_txn_id'
            })
            
            # Add line2_ prefix to all other columns
            rename_dict = {}
            for col in line2_redash_df.columns:
                if col != 'line2_pdd_txn_id':
                    rename_dict[col] = f'line2_{col}'
            line2_redash_df = line2_redash_df.rename(columns=rename_dict)
            
            # Merge with raw_df on line1/2_txn_id = line2_pdd_txn_id
            raw_df = raw_df.merge(
                line2_redash_df,
                left_on='line1/2_txn_id',
                right_on='line2_pdd_txn_id',
                how='left'
            )
            print(f"✅ Merged line2 results: {len(line2_redash_df)} rows")
        else:
            print("⚠️  No line1/2_txn_id values found")
        
        # Step 2: Extract line3_txn_id and run query
        print("\n📋 Step 2: Processing line3_txn_id...")
        line3_txn_ids = raw_df['line3_txn_id'].dropna().unique().tolist()
        print(f"✅ Found {len(line3_txn_ids)} unique line3_txn_id values")
        
        if len(line3_txn_ids) > 0:
            # Execute query for line3
            BATCH_SIZE = 3000
            if len(line3_txn_ids) > BATCH_SIZE:
                print(f"⚠️  Found {len(line3_txn_ids)} IDs (exceeds limit of {BATCH_SIZE})")
                print(f"📦 Splitting into batches...")
                batches = []
                for i in range(0, len(line3_txn_ids), BATCH_SIZE):
                    batches.append(line3_txn_ids[i:i + BATCH_SIZE])
                
                all_results = []
                for batch_num, batch in enumerate(batches, 1):
                    print(f"🔄 Processing line3 batch {batch_num}/{len(batches)}...")
                    batch_df = self.execute_redash_query(batch)
                    all_results.append(batch_df)
                
                line3_redash_df = pd.concat(all_results, ignore_index=True)
            else:
                line3_redash_df = self.execute_redash_query(line3_txn_ids)
            
            # Merge with raw_df on line3_txn_id = pdd_txn_id (no prefix for line3)
            raw_df = raw_df.merge(
                line3_redash_df,
                left_on='line3_txn_id',
                right_on='pdd_txn_id',
                how='left'
            )
            print(f"✅ Merged line3 results: {len(line3_redash_df)} rows")
        else:
            print("⚠️  No line3_txn_id values found")
        
        # Step 3: Map columns
        print("\n🔍 Step 3: Mapping columns...")
        # tester_answer → qc_answer
        if 'tester_answer' in raw_df.columns:
            raw_df['qc_answer'] = raw_df['tester_answer']
        
        # line1/2_answer → line2_cscan_answer
        if 'line1/2_answer' in raw_df.columns:
            raw_df['line2_cscan_answer'] = raw_df['line1/2_answer']
        
        # line3_answer → cscan_answer
        if 'line3_answer' in raw_df.columns:
            raw_df['cscan_answer'] = raw_df['line3_answer']
        
        # created_date → quote_date
        if 'created_date' in raw_df.columns:
            raw_df['quote_date'] = raw_df['created_date']
        
        # Add auditor_answer column (empty for Line3, but needed for compatibility)
        if 'auditor_answer' not in raw_df.columns:
            raw_df['auditor_answer'] = None
        
        print("✅ Column mapping completed")
        
        return raw_df
    
    def generate_report(
        self,
        raw_data_path: str,
        output_folder: str,
        eval_folder: Optional[str] = None,
        include_eval: bool = True,
        source: str = "Cscanpro-Line2"
    ) -> str:
        """
        Generate complete analysis report
        
        Args:
            raw_data_path: Path to raw data CSV
            output_folder: Folder to save output files
            eval_folder: Folder containing eval CSV files (optional)
            include_eval: Whether to include eval results
            source: Source type - "Cscanpro-Line2" or "Cscanpro-Line3"
            
        Returns:
            Path to generated analysis CSV
        """
        print("=" * 60)
        print(f"🚀 Starting Report Generation (Source: {source})")
        print("=" * 60)
        
        # Branch based on source
        if source == "Cscanpro-Line3":
            return self.generate_report_line3(raw_data_path, output_folder, eval_folder, include_eval)
        
        # Original Line2 processing
        # Step 1: Load raw data
        print("\n📖 Step 1: Loading raw data CSV...")
        raw_df = self.load_raw_data_csv(raw_data_path, source=source)
        pdd_txn_ids = raw_df['pdd_txn_id'].dropna().unique().tolist()
        print(f"✅ Found {len(pdd_txn_ids)} unique transaction IDs")
        
        # Step 2: Execute Redash query (with batching if needed)
        print("\n🔄 Step 2: Executing Redash query...")
        
        # Redash API has a limit of 3000 entries per query
        BATCH_SIZE = 3000
        total_ids = len(pdd_txn_ids)
        
        if total_ids > BATCH_SIZE:
            print(f"⚠️  Found {total_ids} transaction IDs (exceeds limit of {BATCH_SIZE})")
            print(f"📦 Splitting into batches of {BATCH_SIZE}...")
            
            # Split into batches
            batches = []
            for i in range(0, total_ids, BATCH_SIZE):
                batch = pdd_txn_ids[i:i + BATCH_SIZE]
                batches.append(batch)
            
            print(f"✅ Created {len(batches)} batch(es): {[len(b) for b in batches]}")
            
            # Execute query for each batch and combine results
            all_results = []
            for batch_num, batch in enumerate(batches, 1):
                print(f"\n🔄 Processing batch {batch_num}/{len(batches)} ({len(batch)} IDs)...")
                batch_df = self.execute_redash_query(batch)
                all_results.append(batch_df)
                print(f"✅ Batch {batch_num} completed: {len(batch_df)} rows")
            
            # Combine all batch results
            print(f"\n🔗 Combining {len(batches)} batch result(s)...")
            redash_df = pd.concat(all_results, ignore_index=True)
            print(f"✅ Combined result: {len(redash_df)} total rows")
        else:
            # No batching needed - execute single query
            redash_df = self.execute_redash_query(pdd_txn_ids)
        
        # Step 3: Join with raw data
        print("\n🔗 Step 3: Joining with raw data...")
        joined_df = self.join_with_raw_data(redash_df, raw_df)
        
        # Step 4: Create final_answer
        print("\n🔍 Step 4: Creating final_answer column...")
        joined_df = self.create_final_answer_column(joined_df)
        
        # Step 4.5: Sort by quote_date BEFORE calculating acc% (important for first-row logic)
        if 'quote_date' in joined_df.columns:
            print("\n📅 Step 4.5: Sorting by quote_date...")
            joined_df = joined_df.sort_values(by='quote_date', na_position='last')
        
        # Step 5: Calculate acc%
        print("\n📊 Step 5: Calculating acc%...")
        joined_df = self.calculate_accuracy(joined_df, 'cscan_answer', 'acc%')
        
        # Step 5.5: Create contributing_sides
        print("\n🔍 Step 5.5: Creating contributing_sides column...")
        joined_df = self.create_contributing_sides(joined_df)
        
        # Step 7: Save UUID files
        print("\n💾 Step 7: Saving UUID JSON files...")
        os.makedirs(output_folder, exist_ok=True)
        self.save_uuid_json_files(joined_df, output_folder)
        
        # Step 8: Join with eval results (if available)
        if include_eval and eval_folder:
            print("\n🔗 Step 8: Joining with eval results...")
            joined_df = self.join_with_eval_results(joined_df, eval_folder)
            
            # Step 9: Create new_cscan_answer
            print("\n🔍 Step 9: Creating new_cscan_answer...")
            joined_df = self.create_new_cscan_answer(joined_df)
            
            # Step 10: Calculate new_acc%
            print("\n📊 Step 10: Calculating new_acc%...")
            joined_df = self.calculate_accuracy(joined_df, 'new_cscan_answer', 'new_acc%')
        
        # Step 11: Create confusion matrices
        print("\n📊 Step 11: Creating confusion matrices...")
        try:
            self.create_confusion_matrices(joined_df, output_folder)
        except Exception as e:
            print(f"⚠️  Warning: Could not create confusion matrices: {e}")
        
        # Step 12: Reorder columns and save final CSV
        print("\n💾 Step 12: Reordering columns and saving analysis CSV...")
        # Reorder based on whether we have eval results
        joined_df = self.reorder_columns(joined_df, include_new_columns=include_eval and eval_folder is not None)
        
        os.makedirs(output_folder, exist_ok=True)
        csv_filename = f"analysis_{datetime.now().strftime('%Y_%m_%d')}.csv"
        csv_path = os.path.join(output_folder, csv_filename)
        joined_df.to_csv(csv_path, index=False)
        print(f"✅ Analysis CSV saved: {csv_path}")
        
        # Step 13: Ensure eval folder exists (empty if no eval data)
        eval_folder_path = os.path.join(output_folder, "eval")
        os.makedirs(eval_folder_path, exist_ok=True)
        # Create .gitkeep or empty file to ensure folder is included in ZIP
        with open(os.path.join(eval_folder_path, ".gitkeep"), 'w') as f:
            f.write("")
        
        print("\n" + "=" * 60)
        print("✅ Report Generation Complete!")
        print("=" * 60)
        
        return csv_path
    
    def create_new_cscan_answer_line3(self, df: pd.DataFrame, cscan_col: str, output_col: str, prefix: str = 'line2_') -> pd.DataFrame:
        """Create new_cscan_answer for Line3 with prefix support"""
        if cscan_col not in df.columns:
            print(f"⚠️  {cscan_col} column not found, skipping {output_col}")
            return df
        
        if self.question_name not in self.threshold_config:
            print(f"⚠️  Question '{self.question_name}' not in threshold config")
            return df
        
        question_thresholds = self.threshold_config[self.question_name]
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        new_answers = []
        
        for idx, row in df.iterrows():
            side_categories = []
            
            for side in sides:
                score_col = f'new_{prefix}{side}_score' if prefix else f'new_{side}_score'
                if score_col not in df.columns:
                    continue
                
                score = row.get(score_col)
                if pd.isna(score):
                    continue
                
                if side not in question_thresholds:
                    continue
                
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(score, side_thresholds)
                side_categories.append((side, category, score))
            
            if not side_categories:
                new_answers.append(None)
                continue
            
            all_categories = [cat for _, cat, _ in side_categories]
            final_answer = None
            for category in severity_order:
                if category in all_categories:
                    final_answer = category
                    break
            
            if final_answer is None:
                final_answer = all_categories[0] if all_categories else None
            
            new_answers.append(final_answer)
        
        result_df = df.copy()
        result_df[output_col] = new_answers
        
        cols = list(result_df.columns)
        if cscan_col in cols:
            cscan_idx = cols.index(cscan_col)
            cols.remove(output_col)
            cols.insert(cscan_idx + 1, output_col)
            result_df = result_df[cols]
        
        return result_df
    
    def create_confusion_matrices_line3(self, df: pd.DataFrame, output_folder: str):
        """Create confusion matrices for Line3 (both line2 and regular)"""
        os.makedirs(output_folder, exist_ok=True)
        
        if 'line2_cscan_answer' in df.columns and 'qc_answer' in df.columns:
            print("📊 Creating confusion matrix for line2_cscan_answer...")
            output_path = os.path.join(output_folder, 'confusion_matrix_line2_acc.png')
            self._create_confusion_matrix(
                df, 'line2_cscan_answer', 'qc_answer',
                output_path, 'Line2 CScan Answer vs Tester Answer'
            )
        
        if 'cscan_answer' in df.columns and 'qc_answer' in df.columns:
            print("📊 Creating confusion matrix for cscan_answer...")
            output_path = os.path.join(output_folder, 'confusion_matrix_acc.png')
            self._create_confusion_matrix(
                df, 'cscan_answer', 'qc_answer',
                output_path, 'CScan Answer vs Tester Answer'
            )
        
        if 'line2_cscan_answer' in df.columns and 'new_line2_cscan_answer' in df.columns:
            print("📊 Creating comparison confusion matrix for line2...")
            output_path = os.path.join(output_folder, 'confusion_matrix_line2_comparison.png')
            self._create_comparison_confusion_matrix(
                df, output_folder,
                predicted_col_before='line2_cscan_answer',
                predicted_col_after='new_line2_cscan_answer',
                actual_col='qc_answer',
                output_filename='confusion_matrix_line2_comparison.png'
            )
        
        if 'cscan_answer' in df.columns and 'new_cscan_answer' in df.columns:
            print("📊 Creating comparison confusion matrix for line3...")
            output_path = os.path.join(output_folder, 'confusion_matrix_comparison.png')
            self._create_comparison_confusion_matrix(
                df, output_folder,
                predicted_col_before='cscan_answer',
                predicted_col_after='new_cscan_answer',
                actual_col='qc_answer',
                output_filename='confusion_matrix_comparison.png'
            )
    
    def reorder_columns_line3(self, df: pd.DataFrame, include_new_columns: bool = False) -> pd.DataFrame:
        """Reorder columns for Line3 data (includes both line2_* and regular columns)"""
        base_order = [
            'line2_pdd_txn_id', 'pdd_txn_id',
            'image_timestamp',
            'line2_top_uuid', 'line2_bottom_uuid', 'line2_right_uuid', 
            'line2_left_uuid', 'line2_back_uuid', 'line2_front_uuid',
            'line2_top_request_body', 'line2_bottom_request_body', 'line2_right_request_body',
            'line2_left_request_body', 'line2_back_request_body', 'line2_front_request_body',
            'line2_top_image_url', 'line2_bottom_image_url', 'line2_right_image_url',
            'line2_left_image_url', 'line2_back_image_url', 'line2_front_image_url',
            'line2_top_result_url', 'line2_bottom_result_url', 'line2_right_result_url',
            'line2_left_result_url', 'line2_back_result_url', 'line2_front_result_url',
            'line2_top_score', 'line2_bottom_score', 'line2_right_score',
            'line2_left_score', 'line2_back_score', 'line2_front_score',
            'top_uuid', 'bottom_uuid', 'right_uuid', 'left_uuid', 'back_uuid', 'front_uuid',
            'top_request_body', 'bottom_request_body', 'right_request_body',
            'left_request_body', 'back_request_body', 'front_request_body',
            'top_image_url', 'bottom_image_url', 'right_image_url',
            'left_image_url', 'back_image_url', 'front_image_url',
            'top_result_url', 'bottom_result_url', 'right_result_url',
            'left_result_url', 'back_result_url', 'front_result_url',
            'top_score', 'bottom_score', 'right_score',
            'left_score', 'back_score', 'front_score',
            'quote_date', 'qc_answer', 'auditor_answer',
            'line2_cscan_answer', 'line2_contributing_sides', 'line2_acc%',
            'cscan_answer', 'contributing_sides', 'acc%',
            'final_answer'
        ]
        
        if include_new_columns:
            new_columns = [
                'new_line2_cscan_answer',
                'new_line2_top_score', 'new_line2_bottom_score', 'new_line2_right_score',
                'new_line2_left_score', 'new_line2_back_score', 'new_line2_front_score',
                'new_line2_top_result_image_url', 'new_line2_bottom_result_image_url',
                'new_line2_right_result_image_url', 'new_line2_left_result_image_url',
                'new_line2_back_result_image_url', 'new_line2_front_result_image_url',
                'new_line2_contributing_sides', 'new_line2_acc%',
                'new_cscan_answer',
                'new_top_score', 'new_bottom_score', 'new_right_score',
                'new_left_score', 'new_back_score', 'new_front_score',
                'new_top_result_image_url', 'new_bottom_result_image_url',
                'new_right_result_image_url', 'new_left_result_image_url',
                'new_back_result_image_url', 'new_front_result_image_url',
                'new_contributing_sides', 'new_acc%'
            ]
            base_order.extend(new_columns)
        
        existing_ordered = [col for col in base_order if col in df.columns]
        extra_cols = [col for col in df.columns if col not in existing_ordered]
        final_order = existing_ordered + extra_cols
        
        return df[final_order]
    
    def generate_report_line3(
        self,
        raw_data_path: str,
        output_folder: str,
        eval_folder: Optional[str] = None,
        include_eval: bool = True
    ) -> str:
        """
        Generate complete analysis report for Line3 source
        
        Args:
            raw_data_path: Path to raw data CSV
            output_folder: Folder to save output files
            eval_folder: Folder containing eval CSV files (optional)
            include_eval: Whether to include eval results
            
        Returns:
            Path to generated analysis CSV
        """
        # Step 1: Load raw data
        print("\n📖 Step 1: Loading raw data CSV (Line3 format)...")
        raw_df = self.load_raw_data_csv(raw_data_path, source="Cscanpro-Line3")
        print(f"✅ Loaded {len(raw_df)} rows")
        
        # Step 2: Process Line3 data (dual queries)
        print("\n🔄 Step 2: Processing Line3 data (dual queries)...")
        joined_df = self.process_line3_data(raw_df)
        
        # Step 3: Create final_answer (for both line2 and regular)
        print("\n🔍 Step 3: Creating final_answer column...")
        # For Line3, final_answer uses qc_answer (tester_answer) since there's no auditor_answer
        if 'qc_answer' in joined_df.columns:
            joined_df['final_answer'] = joined_df['qc_answer']
        else:
            joined_df['final_answer'] = None
        
        # Step 4: Sort by quote_date BEFORE calculating acc%
        if 'quote_date' in joined_df.columns:
            print("\n📅 Step 4: Sorting by quote_date...")
            joined_df = joined_df.sort_values(by='quote_date', na_position='last')
        
        # Step 5: Calculate accuracies
        print("\n📊 Step 5: Calculating accuracies...")
        # Calculate line2_acc% (line2_cscan_answer vs tester_answer)
        if 'line2_cscan_answer' in joined_df.columns and 'qc_answer' in joined_df.columns:
            joined_df = self.calculate_accuracy(joined_df, 'line2_cscan_answer', 'line2_acc%')
        
        # Calculate acc% (cscan_answer vs tester_answer)
        if 'cscan_answer' in joined_df.columns and 'qc_answer' in joined_df.columns:
            joined_df = self.calculate_accuracy(joined_df, 'cscan_answer', 'acc%')
        
        # Step 6: Create contributing_sides (for both line2 and regular)
        print("\n🔍 Step 6: Creating contributing_sides columns...")
        # For line2
        if 'line2_cscan_answer' in joined_df.columns:
            joined_df = self.create_contributing_sides_line3(joined_df, 'line2_cscan_answer', 'line2_contributing_sides', prefix='line2_')
        
        # For line3 (regular)
        if 'cscan_answer' in joined_df.columns:
            joined_df = self.create_contributing_sides(joined_df)
        
        # Step 7: Save UUID files (both line2_* and regular)
        print("\n💾 Step 7: Saving UUID JSON files...")
        os.makedirs(output_folder, exist_ok=True)
        self.save_uuid_json_files_line3(joined_df, output_folder)
        
        # Step 8: Join with eval results (if available)
        if include_eval and eval_folder:
            print("\n🔗 Step 8: Joining with eval results...")
            joined_df = self.join_with_eval_results(joined_df, eval_folder)
            
            # Step 9: Create new_cscan_answer (for both line2 and regular)
            print("\n🔍 Step 9: Creating new_cscan_answer columns...")
            # For line2
            if 'line2_cscan_answer' in joined_df.columns:
                joined_df = self.create_new_cscan_answer_line3(joined_df, 'line2_cscan_answer', 'new_line2_cscan_answer', prefix='line2_')
                if 'new_line2_cscan_answer' in joined_df.columns:
                    joined_df = self.calculate_accuracy(joined_df, 'new_line2_cscan_answer', 'new_line2_acc%')
            
            # For line3 (regular)
            if 'cscan_answer' in joined_df.columns:
                joined_df = self.create_new_cscan_answer(joined_df)
                joined_df = self.calculate_accuracy(joined_df, 'new_cscan_answer', 'new_acc%')
        
        # Step 10: Create confusion matrices
        print("\n📊 Step 10: Creating confusion matrices...")
        try:
            self.create_confusion_matrices_line3(joined_df, output_folder)
        except Exception as e:
            print(f"⚠️  Warning: Could not create confusion matrices: {e}")
        
        # Step 11: Reorder columns and save final CSV
        print("\n💾 Step 11: Reordering columns and saving analysis CSV...")
        joined_df = self.reorder_columns_line3(joined_df, include_new_columns=include_eval and eval_folder is not None)
        
        # Drop unwanted columns from Line3 source
        columns_to_drop = [
            'line1/2_source', 'line3_source', 'line1/2_txn_id', 'line3_txn_id',
            'line1/2_variation', 'line_3_variation', 'tester_variation_id',
            'line1/2_answer', 'line3_answer', 'tester_answer',
            'Matched/Not Matched', 'Unnamed: 14',
            'created_date', 'qr_code'
        ]
        # Drop columns that exist in the dataframe
        existing_columns_to_drop = [col for col in columns_to_drop if col in joined_df.columns]
        if existing_columns_to_drop:
            print(f"🗑️  Dropping {len(existing_columns_to_drop)} unwanted columns: {existing_columns_to_drop}")
            joined_df = joined_df.drop(columns=existing_columns_to_drop)
        
        os.makedirs(output_folder, exist_ok=True)
        csv_filename = f"analysis_{datetime.now().strftime('%Y_%m_%d')}.csv"
        csv_path = os.path.join(output_folder, csv_filename)
        joined_df.to_csv(csv_path, index=False)
        print(f"✅ Analysis CSV saved: {csv_path}")
        
        # Step 12: Ensure eval folder exists
        eval_folder_path = os.path.join(output_folder, "eval")
        os.makedirs(eval_folder_path, exist_ok=True)
        with open(os.path.join(eval_folder_path, ".gitkeep"), 'w') as f:
            f.write("")
        
        print("\n" + "=" * 60)
        print("✅ Report Generation Complete (Line3)!")
        print("=" * 60)
        
        return csv_path

