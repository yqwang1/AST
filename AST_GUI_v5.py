# Created by: yeqing wang
# Date: 2025-03-08 17:33:49
# update: 2025-03-17 23:34:00
# Description: AST_GUI_v5 for another window display at the same time showing all the past trials information.

import pandas as pd
import tkinter as tk
from pathlib import Path


class TrialViewer:
    def __init__(self, excel_file_addr, excel_file_name, sheet_name='template1', skiprows=2):
        self.excel_file = Path(excel_file_addr) / excel_file_name
        self.df = pd.read_excel(self.excel_file, sheet_name=sheet_name, skiprows=skiprows)
        self.finished_early = False
        self.consecutive_ones = 0
        self.output_file = Path(excel_file_addr) / (
                    Path(excel_file_name).stem + "_updated" + Path(excel_file_name).suffix)
        self.history_window = None  # Reference to the history window
        self.history_text = None  # Reference to the history text widget

    def update_history_window(self):
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = tk.Toplevel()
            self.history_window.title("Past Trials")
            self.history_text = tk.Text(self.history_window, height=20, width=200, state=tk.DISABLED)
            self.history_text.pack(padx=10, pady=10)

        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)

        # Select relevant columns
        past_trials = self.df.loc[:self.current_trial_index,
                      ['#', 'side_rwd', 'left_stim', 'right_stim', '+ / X', 'Notes']]

        # Define fixed column widths for proper alignment
        col_widths = {'#': 10, 'side_rwd': 10, 'left_stim': 20, 'right_stim': 20, '+ / X': 10, 'Notes':100 }

        # Convert DataFrame to a formatted string with left-aligned columns
        formatted_rows = []

        # Create header row with aligned column names
        header = "".join(f"{col:<{col_widths[col]}}" for col in past_trials.columns)
        formatted_rows.append(header)
        formatted_rows.append("-" * len(header))  # Add separator line

        # Format each row with left-aligned content
        for _, row in past_trials.iterrows():
            formatted_row = "".join(f"{str(row[col]):<{col_widths[col]}}" for col in past_trials.columns)
            formatted_rows.append(formatted_row)

        # Join rows into a single formatted string
        history_str = "\n".join(formatted_rows)

        # Insert into text widget
        self.history_text.insert(tk.END, history_str)
        self.history_text.config(state=tk.DISABLED)


        '''
        past_trials = self.df.loc[:self.current_trial_index, ['#', 'side_rwd', 'left_stim', 'right_stim', '+ / X', 'Notes']]
        history_str = past_trials.to_string(index=False)    # Convert DataFrame to formatted string for better alignment
        self.history_text.insert(tk.END, history_str)
        self.history_text.config(state=tk.DISABLED)       
        '''


    def show_trial(self, trial_index):
        self.current_trial_index = trial_index  # Track current trial index
        trial_data = self.df.iloc[trial_index]
        window = tk.Toplevel()
        window.title(f"Trial {trial_data['#']}")

        details_text = (
            f"Trial #: {trial_data['#']}\n"
            f"Side Rwd: {trial_data['side_rwd']}\n"
            f"Stim Rwd: {trial_data['stim_rwd']}\n"
            f"Left Stim: {trial_data['left_stim']}\n"
            f"Right Stim: {trial_data['right_stim']}"
        )
        label = tk.Label(window, text=details_text, font=("Arial", 20), anchor="w", justify="left")
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        tk.Label(window, text="+ / X", anchor="w").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        entry_plus = tk.Entry(window)
        entry_plus.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(window, text="Notes", anchor="w").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry_notes = tk.Entry(window)
        entry_notes.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        if self.consecutive_ones > 0:
            consecutive_label = tk.Label(window, text=f"Consecutive trials: {self.consecutive_ones}",
                                         font=("Arial", 14), fg="red")
            consecutive_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        def submit():
            value = entry_plus.get()
            self.df.at[trial_index, '+ / X'] = value
            self.df.at[trial_index, 'Notes'] = entry_notes.get()

            if value == "1":
                self.consecutive_ones += 1
            else:
                self.consecutive_ones = 0

            self.update_history_window()  # Update the history window after submission
            window.destroy()

        submit_button = tk.Button(window, text="Submit", command=submit)
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

        def finish():
            self.finished_early = True
            window.destroy()

        finish_button = tk.Button(window, text="Finish", command=finish)
        finish_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.update_history_window()

        window.wait_window(window)  # Wait for this trial window to close before continuing

    def run_trials(self):
        num_trials = len(self.df)
        for i in range(num_trials):
            self.show_trial(i)
            if self.finished_early:
                print("Early finish requested. Exiting the trial loop.")
                break
        self.df.to_excel(self.output_file, index=False, sheet_name="template1", engine="xlsxwriter")
        print(f"All trials processed. Data saved to {self.output_file}")


if __name__ == "__main__":
    excel_file_addr = "/Users/IrisW/Documents/0Macaskill/AST_codes/"
    excel_file_name = "testing_IDS3.xls"
    trial_viewer = TrialViewer(excel_file_addr, excel_file_name)
    trial_viewer.run_trials()