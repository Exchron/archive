import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def load_koi_data(file_path):
    """
    Load KOI data from CSV file, skipping comment lines that start with '#'
    
    Args:
        file_path (str): Path to the KOI Selected Data.csv file
    
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame
    """
    # Read the file and find the first line that doesn't start with '#'
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Find the header line (first line not starting with '#')
    header_line_index = 0
    for i, line in enumerate(lines):
        if not line.strip().startswith('#'):
            header_line_index = i
            break
    
    # Read the CSV starting from the header line
    df = pd.read_csv(file_path, skiprows=header_line_index, comment='#')
    
    return df

def split_koi_data(input_file, train_output_file, test_output_file, test_size=0.2, random_state=42):
    """
    Split KOI data into 80% train and 20% test sets randomly
    
    Args:
        input_file (str): Path to the input KOI Selected Data.csv file
        train_output_file (str): Path for the training data output file
        test_output_file (str): Path for the test data output file
        test_size (float): Proportion of data to use for testing (default: 0.2 for 20%)
        random_state (int): Random seed for reproducibility (default: 42)
    """
    
    # Load the data
    print(f"Loading data from {input_file}...")
    df = load_koi_data(input_file)
    
    print(f"Total records loaded: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Perform the train-test split
    print(f"Splitting data into {int((1-test_size)*100)}% train and {int(test_size*100)}% test...")
    train_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        random_state=random_state,
        shuffle=True  # Ensure random shuffling
    )
    
    # Save the split datasets
    print(f"Saving training data to {train_output_file}...")
    train_df.to_csv(train_output_file, index=False)
    
    print(f"Saving test data to {test_output_file}...")
    test_df.to_csv(test_output_file, index=False)
    
    # Print summary statistics
    print("\n" + "="*50)
    print("SPLIT SUMMARY")
    print("="*50)
    print(f"Original dataset size: {len(df)} records")
    print(f"Training set size: {len(train_df)} records ({len(train_df)/len(df)*100:.1f}%)")
    print(f"Test set size: {len(test_df)} records ({len(test_df)/len(df)*100:.1f}%)")
    print(f"Random state used: {random_state}")
    
    # Show distribution of target variable if it exists
    if 'koi_disposition' in df.columns:
        print("\nTarget variable distribution:")
        print("Original dataset:")
        print(df['koi_disposition'].value_counts())
        print("\nTraining set:")
        print(train_df['koi_disposition'].value_counts())
        print("\nTest set:")
        print(test_df['koi_disposition'].value_counts())

if __name__ == "__main__":
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "KOI Selected Data.csv")
    train_output_file = os.path.join(current_dir, "KOI-Playground-Train-Data.csv")
    test_output_file = os.path.join(current_dir, "KOI-Playground-Test-Data.csv")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        print("Please make sure the 'KOI Selected Data.csv' file is in the same directory as this script.")
    else:
        # Perform the split
        split_koi_data(
            input_file=input_file,
            train_output_file=train_output_file,
            test_output_file=test_output_file,
            test_size=0.2,  # 20% for test, 80% for train
            random_state=42  # For reproducibility
        )
        
        print(f"\nFiles created successfully:")
        print(f"- Training data: {train_output_file}")
        print(f"- Test data: {test_output_file}")