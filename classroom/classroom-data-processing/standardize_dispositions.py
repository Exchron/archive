import pandas as pd
import os
import shutil
from datetime import datetime

def standardize_dispositions():
    """
    Standardize disposition values across KOI and TESS datasets.
    
    Mapping rules:
    - KOI datasets (KOI Selected Data, KOI Classroom Data):
      * CONFIRMED + CANDIDATE → "candidate"
      * FALSE POSITIVE → "non-candidate"

    - K2 dataset (K2 Data):
        * CONFIRMED + CANDIDATE → "candidate"
        * FALSE POSITIVE → "non-candidate"
    
    - TESS dataset (TESS Classroom Data):
      * (FP, FA) → "non-candidate" 
      * All others (PC, CP, KP, APC) → "candidate"
    
    Replaces original files with standardized versions after creating backups.
    """
    
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    files_to_process = [
        {
            'path': os.path.join(base_dir, "KOI Selected Data.csv"),
            'name': 'KOI Selected Data',
            'column': 'koi_disposition',
            'skip_rows': 33,  # Skip comment lines
            'mapping': {
                'CONFIRMED': 'candidate',
                'CANDIDATE': 'candidate', 
                'FALSE POSITIVE': 'non-candidate'
            }
        },
        {
            'path': os.path.join(base_dir, "classroom-data", "KOI-Classroom-Data.csv"),
            'name': 'KOI Classroom Data',
            'column': 'koi_disposition',
            'skip_rows': 0,
            'mapping': {
                'CONFIRMED': 'candidate',
                'CANDIDATE': 'candidate',
                'FALSE POSITIVE': 'non-candidate'
            }
        },
        {
            'path': os.path.join(base_dir, "K2 Selected Data.csv"),
            'name': 'K2 Selected Data',
            'column': 'disposition',
            'skip_rows': 35,  # Skip comment lines
            'mapping': {
                'CONFIRMED': 'candidate',
                'CANDIDATE': 'candidate',
                'FALSE POSITIVE': 'non-candidate',
                'REFUTED': 'non-candidate'
            }
        },
        {
            'path': os.path.join(base_dir, "classroom-data", "K2-Classroom-Data.csv"),
            'name': 'K2 Classroom Data',
            'column': 'disposition',
            'skip_rows': 0,
            'mapping': {
                'CONFIRMED': 'candidate',
                'CANDIDATE': 'candidate',
                'FALSE POSITIVE': 'non-candidate',
                'REFUTED': 'non-candidate'
            }
        },
        {
            'path': os.path.join(base_dir, "classroom-data", "TESS-Classroom-Data.csv"),
            'name': 'TESS Classroom Data',
            'column': 'tfopwg_disp',
            'skip_rows': 0,
            'mapping': {
                'FP': 'non-candidate',
                'FA': 'non-candidate',
                'PC': 'candidate',
                'CP': 'candidate', 
                'KP': 'candidate',
                'APC': 'candidate'
            }
        }
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for file_info in files_to_process:
        file_path = file_info['path']
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue
            
        print(f"\nProcessing {file_info['name']}...")
        print(f"File: {file_path}")
        
        try:
            # Create backup
            backup_path = f"{file_path}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            print(f"Backup created: {backup_path}")
            
            # Load the data
            if file_info['skip_rows'] > 0:
                # For KOI Selected Data with comment lines
                df = pd.read_csv(file_path, skiprows=file_info['skip_rows'])
            else:
                # For classroom data files
                df = pd.read_csv(file_path)
            
            print(f"Original data loaded: {len(df)} records")
            
            # Check current disposition distribution
            disposition_col = file_info['column']
            print(f"Original {disposition_col} distribution:")
            original_counts = df[disposition_col].value_counts()
            print(original_counts)
            
            # Apply mapping
            df[disposition_col] = df[disposition_col].map(file_info['mapping'])
            
            # Check for any unmapped values
            unmapped = df[disposition_col].isna().sum()
            if unmapped > 0:
                print(f"Warning: {unmapped} values could not be mapped!")
                unmapped_values = df[df[disposition_col].isna()][disposition_col]
                print(f"Unmapped values: {unmapped_values.unique()}")
                continue
            
            # Show new distribution
            print(f"New {disposition_col} distribution:")
            new_counts = df[disposition_col].value_counts()
            print(new_counts)
            
            # Save the modified data
            if file_info['skip_rows'] > 0:
                # For KOI Selected Data, we need to preserve the comment lines
                with open(file_info['path'].replace('.backup_' + timestamp, ''), 'r') as original_file:
                    comment_lines = []
                    for i, line in enumerate(original_file):
                        if i < file_info['skip_rows']:
                            comment_lines.append(line.rstrip('\n'))
                        else:
                            break
                
                # Write comment lines + new data
                with open(file_path, 'w', newline='') as output_file:
                    # Write comment lines
                    for comment_line in comment_lines:
                        output_file.write(comment_line + '\n')
                    
                    # Write CSV data (without writing header again since it's in comments)
                    df.to_csv(output_file, index=False)
            else:
                # For classroom data, simple CSV write
                df.to_csv(file_path, index=False)
            
            print(f"✓ Successfully updated {file_info['name']}")
            
            # Verify the changes by reading back
            verification_df = pd.read_csv(file_path, skiprows=file_info['skip_rows'] if file_info['skip_rows'] > 0 else 0)
            verification_counts = verification_df[disposition_col].value_counts()
            print(f"Verification - Final {disposition_col} distribution:")
            print(verification_counts)
            
        except Exception as e:
            print(f"✗ Error processing {file_info['name']}: {str(e)}")
            # Restore from backup if error occurred
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                print(f"Restored original file from backup")
    
    print(f"\n{'='*60}")
    print("STANDARDIZATION COMPLETE")
    print(f"{'='*60}")
    print("Summary of changes:")
    print("• KOI datasets: CONFIRMED + CANDIDATE → 'candidate', FALSE POSITIVE → 'non-candidate'")
    print("• K2 datasets: CONFIRMED + CANDIDATE → 'candidate', FALSE POSITIVE + REFUTED → 'non-candidate'")
    print("• TESS dataset: FP + FA → 'non-candidate', all others → 'candidate'")
    print(f"• Backup files created with timestamp: {timestamp}")
    print("• Original files have been replaced with standardized versions")

if __name__ == "__main__":
    print("Exoplanet Disposition Standardization Script")
    print("=" * 50)
    print("This script will standardize disposition values across all datasets:")
    print("• KOI Selected Data.csv")
    print("• classroom-data/KOI-Classroom-Data.csv") 
    print("• K2 Selected Data.csv")
    print("• classroom-data/K2-Classroom-Data.csv")
    print("• classroom-data/TESS-Classroom-Data.csv")
    print("\nMapping:")
    print("KOI: CONFIRMED + CANDIDATE → candidate, FALSE POSITIVE → non-candidate")
    print("K2: CONFIRMED + CANDIDATE → candidate, FALSE POSITIVE + REFUTED → non-candidate")
    print("TESS: FP + FA → non-candidate, others → candidate")
    print("\nBackups will be created before making changes.")
    
    response = input("\nProceed with standardization? (y/n): ")
    
    if response.lower().strip() in ['y', 'yes']:
        standardize_dispositions()
    else:
        print("Operation cancelled.")