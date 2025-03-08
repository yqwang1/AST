# Created by: yeqing wang
# Date: 2025-02-28 07:08:52 
# Description: only remain first 1 from each column,
# arduino_csv_curated, to arduino_curated folder

import pandas as pd
import os
from pathlib import Path


def process_csv(file_path, output_folder):
    df = pd.read_csv(file_path)

    # Convert timestamp to pandas datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Process each column to keep only the first occurrence of 1 in consecutive sequences
    for col in df.columns:
        if col != 'timestamp':  # Skip timestamp column
            df[col] = (df[col].diff() != 0).astype(int) * df[col]

    # Remove rows where all numeric columns are 0 (except timestamp)
    df = df[(df.iloc[:, :-1] != 0).any(axis=1)]

    # Save processed file
    output_file = output_folder / f"processed_{Path(file_path).name}"
    df.to_csv(output_file, index=False)
    print(f"Processed and saved: {output_file}")


def process_folder(input_folder, output_folder):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for file in input_folder.glob("*.csv"):
        process_csv(file, output_folder)

    print("Processing complete!")


# Example usage
if __name__ == "__main__":
    input_folder = "/Users/IrisW/Documents/0Macaskill/AST_data/AM_GH3/arduino/arduino_clean"
    output_folder = "/Users/IrisW/Documents/0Macaskill/AST_data/AM_GH3/arduino/arduino_curated"
    process_folder(input_folder, output_folder)
