import pandas as pd
import os
import numpy as np

# Define file paths
input_file = os.path.join("disposition-combined", "KOI Modified Data.csv")
output_file = "KOI Selected 2000 Signals.csv"

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(current_dir, input_file)
output_path = os.path.join(current_dir, output_file)

# Read the CSV file with comment lines skipped
print(f"Reading data from: {input_path}")
df = pd.read_csv(input_path, comment='#')

# Define what constitutes a "clean signal" for candidates - all false positive flags are 0
clean_signals_candidates = (
    (df['koi_fpflag_nt'] == 0) & 
    (df['koi_fpflag_ss'] == 0) & 
    (df['koi_fpflag_co'] == 0) & 
    (df['koi_fpflag_ec'] == 0) &
    (df['koi_disposition'] == 'CANDIDATE')
)

# For false positives, we'll relax the criteria to get 1000 entries with highest SNR
false_positive_signals = (df['koi_disposition'] == 'FALSE POSITIVE')

# Get candidates with clean signals
candidates = df[clean_signals_candidates].copy()

# Get all false positives (regardless of flags)
false_positives = df[false_positive_signals].copy()

print(f"Total entries: {len(df)}")
print(f"Clean candidate signals: {len(candidates)}")
print(f"All false positive signals: {len(false_positives)}")

# Check if we have enough data
if len(candidates) < 1000:
    print(f"WARNING: Only {len(candidates)} candidates with clean signals are available (less than 1000 requested)")
    num_candidates = len(candidates)
else:
    num_candidates = 1000

if len(false_positives) < 1000:
    print(f"WARNING: Only {len(false_positives)} false positives are available (less than 1000 requested)")
    num_false_positives = len(false_positives)
else:
    num_false_positives = 1000

# Sort by SNR (koi_model_snr) in descending order and take the top entries
top_candidates = candidates.sort_values('koi_model_snr', ascending=False).head(num_candidates)
top_false_positives = false_positives.sort_values('koi_model_snr', ascending=False).head(num_false_positives)

print(f"\nSelected {len(top_candidates)} candidates with highest SNR")
print(f"Selected {len(top_false_positives)} false positives with highest SNR")

# Combine the selected data
selected_data = pd.concat([top_candidates, top_false_positives])

# Shuffle the data to randomize the order
selected_data = selected_data.sample(frac=1, random_state=42)

print(f"\nTotal selected entries: {len(selected_data)}")

# SNR statistics
print("\nSignal-to-Noise Ratio (SNR) statistics for selected data:")
print(f"Candidates - Min SNR: {top_candidates['koi_model_snr'].min():.2f}, Max SNR: {top_candidates['koi_model_snr'].max():.2f}, Mean SNR: {top_candidates['koi_model_snr'].mean():.2f}")
print(f"False Positives - Min SNR: {top_false_positives['koi_model_snr'].min():.2f}, Max SNR: {top_false_positives['koi_model_snr'].max():.2f}, Mean SNR: {top_false_positives['koi_model_snr'].mean():.2f}")

# Read the original file to get comment lines
with open(input_path, 'r') as f:
    comments = []
    for line in f:
        if line.startswith('#'):
            comments.append(line)
        else:
            break

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Write the comments to the output file
with open(output_path, 'w') as f:
    for comment in comments:
        f.write(comment)
    # Add an additional comment line explaining this dataset
    f.write(f"# This file contains {len(top_candidates)} candidates with clean signals (all FP flags = 0) and {len(top_false_positives)} false positives, selected based on highest Signal-to-Noise Ratio\n#\n")

# Append the dataframe data to the output file
selected_data.to_csv(output_path, mode='a', index=False)

print(f"\nSelected data has been saved to: {output_file}")