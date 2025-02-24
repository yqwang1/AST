# Created by: yeqing wang
# Date: 2025-02-23 20:44:01 
# Description: AST_GUI, simple version of GUI

import pandas as pd
import tkinter as tk

# ----------------------------
# Step 1: Read the Excel file
# ----------------------------
# We assume the table (with headers: "#", "side_rwd", "left_stim", "right_stim", "stim_rwd", "Done?", "+ / X", "Notes")
# starts at row 4 in the sheet "Data". Adjust skiprows if needed.
excel_file = "/Users/IrisW/Documents/0Macaskill/AST_codes/ctrl_testing/testing_IDS3.xls"
df = pd.read_excel(excel_file, sheet_name='template1', skiprows=2)
print(df)
print("Columns in the DataFrame:", df.columns.tolist())

# Global flag to determine if the user wants to finish early
finished_early = False

# ----------------------------
# Step 2: Create a function to display prompt for a trial
# ----------------------------
def show_trial(trial_index):
    global finished_early  # allow modification of the global flag

    # Get the row for the current trial
    trial_data = df.iloc[trial_index]

    # Create a new window for this trial
    window = tk.Tk()
    window.title(f"Trial {trial_data['number']}")

    # Display trial details
    details_text = (
        f"Trial Number: {trial_data['number']}\n"
        f"Side Rwd: {trial_data['side_rwd']}\n"
        f"Stim Rwd: {trial_data['stim_rwd']}\n"
        f"Left Stim: {trial_data['left_stim']}\n"
        f"Right Stim: {trial_data['right_stim']}"
    )
    label = tk.Label(window, text=details_text, font=("Arial", 20), anchor="w", justify="left")
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    # Create left-aligned labels and entry fields for the blank cells.
    tk.Label(window, text="Done?", anchor="w").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_done = tk.Entry(window)
    entry_done.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    tk.Label(window, text="+ / X", anchor="w").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_plus = tk.Entry(window)
    entry_plus.grid(row=2, column=1, sticky="w", padx=10, pady=5)

    tk.Label(window, text="Notes", anchor="w").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    entry_notes = tk.Entry(window)
    entry_notes.grid(row=3, column=1, sticky="w", padx=10, pady=5)

    # Define what happens when the user clicks the Submit button
    def submit():
        # Save the user's input into the DataFrame
        df.at[trial_index, 'Done?'] = entry_done.get()
        df.at[trial_index, '+ / X'] = entry_plus.get()
        df.at[trial_index, 'Notes'] = entry_notes.get()
        window.destroy()  # Close the current prompt window

    submit_button = tk.Button(window, text="Submit", command=submit)
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Define the finish function to allow early exit
    def finish():
        global finished_early
        finished_early = True
        window.destroy()  # Close the current prompt window

    finish_button = tk.Button(window, text="Finish", command=finish)
    finish_button.grid(row=5, column=0, columnspan=2, pady=10)

    window.mainloop()

# ----------------------------
# Step 3: Loop through each trial and show the prompt
# ----------------------------
num_trials = len(df)
for i in range(num_trials):
    show_trial(i)
    if finished_early:
        print("Early finish requested. Exiting the trial loop.")
        break

# ----------------------------
# Step 4: Save the updated responses back to Excel
# ----------------------------
# This saves only the table. If you need to preserve the metadata rows,
# you might consider a more advanced approach using openpyxl.
output_file = "/Users/IrisW/Documents/0Macaskill/AST_codes/ctrl_testing/testing_IDS3_updated.xls"
df.to_excel(output_file, index=False, sheet_name="template1", engine="xlsxwriter")

print(f"All trials processed. Data saved to {output_file}")
