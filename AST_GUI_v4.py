# Created by: yeqing wang
# Date: 2025-02-26 21:39:05
# Description: AST_GUI_v4

import pandas as pd
import tkinter as tk
from pathlib import Path


class TrialViewer:
    def __init__(self, excel_file_addr, excel_file_name, sheet_name='template1', skiprows=2):
        self.excel_file = Path(excel_file_addr) / excel_file_name
        self.df = pd.read_excel(self.excel_file, sheet_name=sheet_name, skiprows=skiprows)
        self.finished_early = False
        self.consecutive_ones = 0
        self.output_file = Path(excel_file_addr) / (Path(excel_file_name).stem + "_updated" + Path(excel_file_name).suffix)

    def show_trial(self, trial_index):
        trial_data = self.df.iloc[trial_index]
        window = tk.Tk()
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
            consecutive_label = tk.Label(window, text=f"Consecutive trials: {self.consecutive_ones}", font=("Arial", 14), fg="red")
            consecutive_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        def submit():
            value = entry_plus.get()
            self.df.at[trial_index, '+ / X'] = value
            self.df.at[trial_index, 'Notes'] = entry_notes.get()

            if value == "1":
                self.consecutive_ones += 1
            else:
                self.consecutive_ones = 0

            window.destroy()

        submit_button = tk.Button(window, text="Submit", command=submit)
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

        def finish():
            self.finished_early = True
            window.destroy()

        finish_button = tk.Button(window, text="Finish", command=finish)
        finish_button.grid(row=6, column=0, columnspan=2, pady=10)

        window.mainloop()

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
    excel_file_addr = "/Users/IrisW/Documents/0Macaskill/AST_codes/ctrl_testing/"
    excel_file_name = "testing_IDS3.xls"
    trial_viewer = TrialViewer(excel_file_addr, excel_file_name)
    trial_viewer.run_trials()
