import pandas as pd
import lightkurve as lk
import os
import time
import concurrent.futures
from tqdm import tqdm  # For progress bar

def download_lightkurve_data(kepler_id, output_dir):
    """
    Download light curve data for a given Kepler ID and save to CSV
    
    Parameters:
    -----------
    kepler_id : str
        The Kepler ID to search for
    output_dir : str
        Directory to save the output CSV file
        
    Returns:
    --------
    dict
        Dictionary with results info
    """
    try:
        # Check if file already exists (for resuming)
        kepler_id_clean = str(kepler_id).strip()
        output_file = os.path.join(output_dir, f"kepler_{kepler_id_clean}_lightkurve.csv")
        
        if os.path.exists(output_file):
            return {
                'kepler_id': kepler_id_clean,
                'success': True,
                'output_file': output_file,
                'status': 'Skipped (already exists)'
            }
            
        # Search directly using Kepler ID
        search_term = f"KIC {kepler_id_clean}"
        
        # Search for light curves
        search_result = lk.search_lightcurve(search_term, mission='Kepler')
        
        if len(search_result) > 0:
            # Download the first (or best) light curve
            lc = search_result[0].download()
        else:
            return {
                'kepler_id': kepler_id_clean,
                'success': False,
                'output_file': None,
                'status': 'No light curve found'
            }
            
        # Convert to pandas DataFrame
        df = lc.to_pandas()
        
        # Add Kepler ID as a column for identification
        df['kepler_id'] = kepler_id_clean
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        return {
            'kepler_id': kepler_id_clean,
            'success': True,
            'output_file': output_file,
            'status': 'Downloaded'
        }
    
    except Exception as e:
        return {
            'kepler_id': kepler_id_clean,
            'success': False,
            'output_file': None,
            'status': f'Error: {str(e)}'
        }

def main():
    # Path to the input CSV file containing KOI IDs
    input_file = "koi_data.csv"
    
    # Directory to save output files
    output_dir = "lightkurve_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Summary file to track all processed KOIs
    summary_file = os.path.join(output_dir, "kepler_lightkurve_summary.csv")
    
    # Load the input CSV file
    df_input = pd.read_csv(input_file)
    
    # Use 'kepid' column as the source of Kepler IDs
    koi_column = 'kepid'
    
    if koi_column not in df_input.columns:
        print(f"Column '{koi_column}' not found in the input CSV.")
        print("Available columns:", df_input.columns.tolist())
        koi_column = input("Please enter the column name containing Kepler IDs: ")
        if koi_column not in df_input.columns:
            print(f"Column '{koi_column}' not found. Exiting.")
            return
    
    print(f"Using column '{koi_column}' for Kepler IDs")
    
    # Load previous results if available (for resuming)
    existing_results = []
    if os.path.exists(summary_file):
        try:
            existing_df = pd.read_csv(summary_file)
            existing_results = existing_df.to_dict('records')
            print(f"Loaded {len(existing_results)} existing results from summary file")
        except:
            print("Could not load existing summary file, starting fresh")
    
    # Get list of IDs to process
    all_kepler_ids = [str(row[koi_column]) for _, row in df_input.iterrows()]
    
    # Skip already processed IDs if we have existing results
    if existing_results:
        processed_ids = {str(result['kepler_id']) for result in existing_results}
        kepler_ids = [kid for kid in all_kepler_ids if str(kid) not in processed_ids]
        print(f"Skipping {len(processed_ids)} already processed IDs")
        
        # Add existing results to our results list so they appear in final summary
        results = existing_results.copy()
    else:
        kepler_ids = all_kepler_ids
        results = []
        
    # Double check for files that exist but aren't in the summary file
    # This can happen if a previous run was interrupted after saving the file but before updating the summary
    files_to_check = [os.path.join(output_dir, f"kepler_{kid}_lightkurve.csv") for kid in kepler_ids]
    existing_files = [f for f in files_to_check if os.path.exists(f)]
    
    if existing_files:
        print(f"Found {len(existing_files)} additional files that already exist but weren't in summary")
        # Extract IDs from filenames and add to processed list
        for file_path in existing_files:
            kepler_id_clean = os.path.basename(file_path).replace("kepler_", "").replace("_lightkurve.csv", "")
            results.append({
                'kepler_id': kepler_id_clean,
                'success': True,
                'output_file': file_path,
                'status': 'Found existing file'
            })
        
        # Update kepler_ids list to remove these
        processed_file_ids = {os.path.basename(f).replace("kepler_", "").replace("_lightkurve.csv", "") for f in existing_files}
        kepler_ids = [kid for kid in kepler_ids if kid not in processed_file_ids]
    
    # Optional: Allow processing a subset (for testing or chunking)
    limit = None  # Set to a number to process only that many entries
    if limit:
        kepler_ids = kepler_ids[:limit]
        print(f"Processing only the first {limit} Kepler IDs")
    
    print(f"Preparing to download data for {len(kepler_ids)} Kepler IDs")
    
    # Number of parallel workers (adjust based on your system capabilities)
    max_workers = 20  # Increased for faster downloading
    
    # results list is now initialized earlier when loading existing results
    completed_count = 0
    save_interval = 50  # Save progress every 50 completed downloads
    
    # Use ThreadPoolExecutor for parallel downloading
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_id = {executor.submit(download_lightkurve_data, kid, output_dir): kid for kid in kepler_ids}
        
        # Process results as they complete with progress bar
        for future in tqdm(concurrent.futures.as_completed(future_to_id), total=len(kepler_ids), desc="Downloading"):
            kid = future_to_id[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                results.append({
                    'kepler_id': kid,
                    'success': False,
                    'output_file': None,
                    'status': f'Exception: {exc}'
                })
            
            # Periodically save progress
            completed_count += 1
            if completed_count % save_interval == 0:
                temp_df = pd.DataFrame(results)
                temp_df.to_csv(summary_file, index=False)
                print(f"\nIntermediate progress saved: {completed_count}/{len(kepler_ids)} completed")
    
    # Create a summary DataFrame and save it
    summary_df = pd.DataFrame(results)
    summary_df.to_csv(summary_file, index=False)
    
    # Print summary statistics
    successful = summary_df['success'].sum()
    print(f"\nSummary saved to {summary_file}")
    print(f"Successfully downloaded {successful} out of {len(summary_df)} light curves")
    
    # Status breakdown
    status_counts = summary_df['status'].value_counts()
    print("\nStatus breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
        
    # Performance tip for next run
    error_rate = 1.0 - (successful / len(summary_df)) if len(summary_df) > 0 else 0
    if error_rate > 0.5 and max_workers > 5:
        print(f"\nWARNING: High error rate ({error_rate:.1%}). Consider reducing max_workers to {max_workers // 2} in your next run.")

if __name__ == "__main__":
    main()