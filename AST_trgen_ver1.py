# Created by: yeqing wang
# Date: 2025-02-18 11:32:57
# Description: AST_trgen_ver1, psuedo random trials generator ver 1.

import random
import pandas as pd


class AST_trgen_ver1:
    def __init__(self, sequence_length: int,
                 max_streak_seq1: int, bias_correction_seq1: float,
                 max_streak_seq2: int, bias_correction_seq2: float,
                 reward_stim_options: list, reward_stim_options_mac: list):
        """
        Initialize the generator with sequence parameters and reward stimulus options.

        Parameters:
            sequence_length (int): Length of the sequences to be generated.
            max_streak_seq1 (int): Maximum streak allowed for the first sequence.
            bias_correction_seq1 (float): Bias threshold for generating the first sequence.
            max_streak_seq2 (int): Maximum streak allowed for the second sequence.
            bias_correction_seq2 (float): Bias threshold for generating the second sequence.
            reward_stim_options (list): List of reward stimuli (e.g., ["Anise", "Ginger"]).
            reward_stim_options_mac (list): List of reward stimulus pair options, e.g.,
                [
                    ["Anise/Cord", "Ginger/Metal Strip"],
                    ["Anise/Metal Strip", "Ginger/Cord"]
                ]
        """
        self.sequence_length = sequence_length
        self.max_streak_seq1 = max_streak_seq1
        self.bias_correction_seq1 = bias_correction_seq1
        self.max_streak_seq2 = max_streak_seq2
        self.bias_correction_seq2 = bias_correction_seq2
        self.reward_stim_options = reward_stim_options
        self.reward_stim_options_mac = reward_stim_options_mac
        self.df = None  # To store the final DataFrame

    def generate_biased_sequence(self, length: int, bias_correction: float) -> list:
        """
        Generate a random binary sequence (0s and 1s) based on the given bias_correction.
        """
        return [1 if random.random() > bias_correction else 0 for _ in range(length)]

    def rearrange_sequence(self, sequence: list, max_streak: int) -> list:
        """
        Rearrange the sequence to ensure that there are no more than max_streak
        consecutive identical numbers.
        """
        i = 0
        while i <= len(sequence) - max_streak:
            if all(sequence[i] == sequence[i + j] for j in range(max_streak)):
                swap_idx = next((j for j in range(i + max_streak, len(sequence))
                                 if sequence[j] != sequence[i]), None)
                if swap_idx is not None:
                    sequence[i + max_streak - 1], sequence[swap_idx] = sequence[swap_idx], sequence[i + max_streak - 1]
                else:
                    break  # No valid swap found, exit the loop
            i += 1
        return sequence

    def generate_sequence(self, length: int, max_streak: int, bias_correction: float) -> list:
        """
        Generate a biased binary sequence and rearrange it to avoid long streaks.
        """
        seq = self.generate_biased_sequence(length, bias_correction)
        return self.rearrange_sequence(seq, max_streak)

    def assign_reward_side(self, sequence: list) -> list:
        """
        Assign reward sides based on the binary sequence:
            0 -> "Left"
            1 -> "Right"
        """
        return ["Left" if num == 0 else "Right" for num in sequence]

    def choose_reward_stimulus(self) -> str:
        """
        Randomly select one reward stimulus from the provided reward_stim_options.
        """
        return random.choice(self.reward_stim_options)

    def create_reward_dataframe(self, seq: list, seq2: list, reward_stim: str) -> pd.DataFrame:
        """
        Create a DataFrame combining reward side assignments and stimulus pair selections.

        For each trial, determine which side (left/right) receives the reward stimulus based
        on the reward side assignment.
        """
        reward_side = self.assign_reward_side(seq)
        selected_pairs = [self.reward_stim_options_mac[i] for i in seq2]

        df = pd.DataFrame({
            "reward_side": reward_side,
            "reward_stim": [reward_stim] * len(seq2),
            "selected_pairs": selected_pairs
        })

        def assign_stimuli(row):
            left, right = row["selected_pairs"]
            reward = row["reward_stim"]
            # Identify which element contains the reward stimulus
            reward_stimulus = left if reward in left else right
            other_stimulus = right if reward in left else left
            # Return stimuli order based on the reward side assignment
            return (reward_stimulus, other_stimulus) if row["reward_side"] == "Left" else (
                other_stimulus, reward_stimulus)

        df[["left_stim", "right_stim"]] = df.apply(assign_stimuli, axis=1, result_type="expand")
        df.drop(columns=["selected_pairs"], inplace=True)
        return df

    def save_dataframe_to_csv(self, file_path: str) -> None:
        """
        Save the generated DataFrame to a CSV file at the specified file path.
        """
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
        else:
            print("No DataFrame available to save. Please run the generator first.")

    def run(self, csv_path: str = None) -> None:
        """
        Generate sequences, choose a reward stimulus, create the DataFrame,
        and print the results.
        Parameters:
            csv_path (str, optional): If provided, the DataFrame will be saved to this CSV file.
        """
        # Generate sequences using provided parameters
        seq = self.generate_sequence(self.sequence_length, self.max_streak_seq1, self.bias_correction_seq1)
        seq2 = self.generate_sequence(self.sequence_length, self.max_streak_seq2, self.bias_correction_seq2)

        # Display sequence details
        print("Sequence 1:", seq)
        print("Zeros:", seq.count(0), "Ones:", seq.count(1))
        print("Sequence 2:", seq2)
        print("Zeros:", seq2.count(0), "Ones:", seq2.count(1))

        # Randomly select the reward stimulus
        reward_stim = self.choose_reward_stimulus()
        print("Selected Reward Stimulus:", reward_stim)

        # Create and display the final DataFrame
        self.df = self.create_reward_dataframe(seq, seq2, reward_stim)
        print("Final DataFrame:")
        print(self.df)

        # Save to CSV if a file path is provided
        if csv_path:
            self.save_dataframe_to_csv(csv_path)


if __name__ == '__main__':
    # Define inputs for reward stimulus options
    reward_stim_options = ["Anise", "Ginger"]
    reward_stim_options_mac = [
        ["Anise/Cord", "Ginger/Metal Strip"],
        ["Anise/Metal Strip", "Ginger/Cord"]
    ]

    # Create an instance of AST_trgen_ver1 with specified parameters
    generator = AST_trgen_ver1(
        sequence_length=55,
        max_streak_seq1=4,
        bias_correction_seq1=0.5,
        max_streak_seq2=3,
        bias_correction_seq2=0.5,
        reward_stim_options=reward_stim_options,
        reward_stim_options_mac=reward_stim_options_mac
    )

    # Run the generator to execute the process
    csv_path = "/Users/IrisW/Documents/0Macaskill/AST_codes/IDS3_2_20250221_2.csv"
    generator.run(csv_path)
    print("Done")
