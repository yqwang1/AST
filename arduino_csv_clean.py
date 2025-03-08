# Created by: yeqing wang
# Date: 2025-02-28 05:44:03 
# Description: removed machine noise from raw data to arduino_clean folder.
# set readable columns from the raw to "start, digW, digR, eat and timestamp" columns.
# needs to update:
# check if it is removing the weird pair in the middle;
# only 4 numbers in the first column and paired with timestamp are good ones to use.
# 2. change the name of output file.


import pandas as pd
import re
import os


def process_arduino_data(file_path):
    """
    Processes a single CSV file to extract relevant data.

    Parameters:
    file_path (str): Path to the input CSV file.

    Returns:
    pd.DataFrame: A DataFrame containing columns 'start', 'digW', 'digR', 'eat', and 'timestamp'.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data = []
    pattern = re.compile(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*,\s*([\d\-T:+.]+)")

    for line in lines:
        match = pattern.search(line)
        if match:
            data.append(match.groups())

    df_cleaned = pd.DataFrame(data, columns=["start", "digW", "digR", "eat", "timestamp"])
    df_cleaned[["start", "digW", "digR", "eat"]] = df_cleaned[["start", "digW", "digR", "eat"]].astype(int)

    # Convert timestamp column to datetime format
    df_cleaned["timestamp"] = pd.to_datetime(df_cleaned["timestamp"])

    return df_cleaned


def process_folder(input_folder, output_folder):
    """
    Processes all CSV files in a folder and saves the cleaned files.

    Parameters:
    input_folder (str): Path to the folder containing raw CSV files.
    output_folder (str): Path to the folder where processed files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create output folder if it doesn't exist

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".csv"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)

            df_processed = process_arduino_data(input_path)
            df_processed.to_csv(output_path, index=False)

            print(f"Processed and saved: {file_name}")


# Example usage:
if __name__ == "__main__":
    input_folder = "/Users/IrisW/Documents/0Macaskill/AST_data/AM_GH3/arduino/arduino_raw"  # Replace with actual input folder path
    output_folder = "/Users/IrisW/Documents/0Macaskill/AST_data/AM_GH3/arduino/arduino_clean"  # Replace with desired output folder path
    process_folder(input_folder, output_folder)
