# Created by: yeqing wang
# Date: 2025-02-28 07:40:33 
# Description: ctrl_test_anal_1, some random plot analysis for testing AST protocol.
#"/Users/IrisW/Documents/0Macaskill/AST_codes/20250217_ctrl_testing/AM_GH1/arduino_curated_yw"

import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# Define the folder containing the CSV files
folder_path = "/Users/IrisW/Documents/0Macaskill/AST_codes/20250217_ctrl_testing/AM_GH0/arduino_curated_yw"  # Update this to the actual path

# Define x-axis categories
categories = ["SD1", "SD2", "CD1", "CD2", "IDS1_1", "IDS1_2", "IDS2_1", "IDS2_2",
              "IDS3_1", "IDS3_2", "IDS4_1", "IDS4_2", "EDS_1", "EDS_2", "EDSR", "NoRule"]

# Subset of categories for the second plot
subset_categories = ["SD2", "CD1", "IDS1_1", "IDS2_1", "IDS3_1", "IDS4_1", "EDS_1", "EDSR", "NoRule"]

# Dictionary to store counts
counts = {category: 0 for category in categories}

# Function to extract timestamp from filename
def extract_timestamp(filename):
    match = re.search(r'processed_arduino_input(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2})', filename)
    return match.group(1) if match else ""

# Get list of CSV files sorted by extracted timestamp
csv_files = sorted(
    [f for f in os.listdir(folder_path) if f.endswith(".csv")],
    key=lambda x: extract_timestamp(x)
)

# Read each CSV file in order and count occurrences of 1 in the "start" column
for idx, file in enumerate(csv_files):
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    if "start" in df.columns:
        count_ones = (df["start"] == 1).sum()
        if idx < len(categories):  # Ensure index is within range of categories
            counts[categories[idx]] += count_ones

# Convert to lists for plotting
x_labels = list(counts.keys())
y_values = list(counts.values())

# Plot the first chart
plt.figure(figsize=(12, 6))
plt.plot(x_labels, y_values, marker='o', linestyle='-', color='b')
plt.xlabel("Categories")
plt.ylabel("trials")
plt.title("AM_GH0")
plt.xticks(rotation=45)
plt.ylim(0, 50)
plt.show()

# Filter data for the second plot
filtered_counts = {k: counts[k] for k in subset_categories}

# Plot the second chart
plt.figure(figsize=(10, 5))
plt.plot(filtered_counts.keys(), filtered_counts.values(), marker='o', linestyle='-', color='r')
plt.xlabel("Categories")
plt.ylabel("trials")
plt.title("AM_GM0")
plt.xticks(rotation=45)
plt.ylim(0, 50)
plt.show()
