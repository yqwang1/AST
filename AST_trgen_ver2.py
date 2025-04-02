# Created by: yeqing wang
# Date: 2025-03-18 12:09:53
# Update:2025-04-02 14:30:52
# Description: AST_trgen_ver2,updating:  writing data into target xls directly; check bias with bin size of 8 trials.(left vs right;
# one-pair vs another pair; each pair is stick to on position?
# 0. mapping to correct format of files.
# 1. every 8 block evenly distributed two pair on two sides (two pair never be 1/7; left and right never be bias to one side)
# 2. rwd location L/R, also depends on previous L/R, better not repeat pattern(hard), not 1/7

'''
import random
import pandas as pd
from collections import Counter


class AST_trgen_ver1:
    def __init__(self, sequence_length: int,
                 max_streak_seq1: int, bias_correction_seq1: float,
                 max_streak_seq2: int, bias_correction_seq2: float,
                 reward_stim_options: list, reward_stim_options_mac: list):
        self.sequence_length = sequence_length
        self.max_streak_seq1 = max_streak_seq1
        self.bias_correction_seq1 = bias_correction_seq1
        self.max_streak_seq2 = max_streak_seq2
        self.bias_correction_seq2 = bias_correction_seq2
        self.reward_stim_options = reward_stim_options
        self.reward_stim_options_mac = reward_stim_options_mac
        self.df = None

    def generate_biased_sequence(self, length: int, bias_correction: float) -> list:
        return [1 if random.random() > bias_correction else 0 for _ in range(length)]

    def rearrange_sequence(self, sequence: list, max_streak: int) -> list:
        i = 0
        while i <= len(sequence) - max_streak:
            if all(sequence[i] == sequence[i + j] for j in range(max_streak)):
                swap_idx = next((j for j in range(i + max_streak, len(sequence))
                                 if sequence[j] != sequence[i]), None)
                if swap_idx is not None:
                    sequence[i + max_streak - 1], sequence[swap_idx] = sequence[swap_idx], sequence[i + max_streak - 1]
                else:
                    break
            i += 1
        return sequence

    def generate_sequence(self, length: int, max_streak: int, bias_correction: float) -> list:
        while True:
            seq = self.generate_biased_sequence(length, bias_correction)
            seq = self.rearrange_sequence(seq, max_streak)
            if self.validate_no_long_pattern(seq):
                return seq

    def validate_no_long_pattern(self, sequence: list) -> bool:
        pattern_str = ''.join(['L' if x == 0 else 'R' for x in sequence])
        for i in range(3, len(pattern_str)//2 + 1):
            pattern = pattern_str[:i]
            if pattern * (len(pattern_str) // len(pattern)) == pattern_str[:len(pattern) * (len(pattern_str) // len(pattern))]:
                return False
        return True

    def assign_reward_side(self, sequence: list) -> list:
        return ["Left" if num == 0 else "Right" for num in sequence]

    def choose_reward_stimulus(self) -> str:
        return random.choice(self.reward_stim_options)

    def create_reward_dataframe(self, seq: list, seq2: list, reward_stim: str) -> pd.DataFrame:
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
            reward_stimulus = left if reward in left else right
            other_stimulus = right if reward in left else left
            return (reward_stimulus, other_stimulus) if row["reward_side"] == "Left" else (other_stimulus, reward_stimulus)

        df[["left_stim", "right_stim"]] = df.apply(assign_stimuli, axis=1, result_type="expand")
        df.drop(columns=["selected_pairs"], inplace=True)

        return df

    def validate_bins(self, df: pd.DataFrame) -> bool:
        for i in range(0, len(df), 8):
            bin_df = df.iloc[i:i+8]
            if len(bin_df) < 8:
                break
            pairs = [(l, r) for l, r in zip(bin_df['left_stim'], bin_df['right_stim'])]
            pair_types = [tuple(sorted([l, r])) for l, r in pairs]
            pair_counts = Counter(pair_types)
            if len(pair_counts) < 2 or min(pair_counts.values()) < 2:
                return False

            rwd_sides = bin_df.loc[bin_df["reward_stim"].isin(bin_df["left_stim"] + bin_df["right_stim"]), "reward_side"]
            if abs(list(rwd_sides).count("Left") - list(rwd_sides).count("Right")) > 2:
                return False

            rwd_pattern = ''.join(['L' if side == 'Left' else 'R' for side in bin_df["reward_side"]])
            if any(rwd_pattern[j:j+3] == rwd_pattern[j+3:j+6] for j in range(len(rwd_pattern)-5)):
                return False

        return True

    def save_dataframe_to_csv(self, file_path: str) -> None:
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
        else:
            print("No DataFrame available to save. Please run the generator first.")

    def run(self, csv_path: str = None) -> None:
        max_attempts = 1000
        for attempt in range(max_attempts):
            seq = self.generate_sequence(self.sequence_length, self.max_streak_seq1, self.bias_correction_seq1)
            seq2 = self.generate_sequence(self.sequence_length, self.max_streak_seq2, self.bias_correction_seq2)
            reward_stim = self.choose_reward_stimulus()
            df = self.create_reward_dataframe(seq, seq2, reward_stim)
            if df is not None and self.validate_bins(df):
                self.df = df
                break
        else:
            raise RuntimeError("Failed to generate a valid sequence within retry limit.")

        print("Final DataFrame:")
        print(self.df)

        if csv_path:
            self.save_dataframe_to_csv(csv_path)


if __name__ == '__main__':
    reward_stim_options = ["Whshred", "Card"]
    reward_stim_options_mac = [
        ["Lemon/Whshred", "Anise/Card"],
        ["Lemon/Card", "Anise/Whshred"]
    ]

    generator = AST_trgen_ver1(
        sequence_length=55,
        max_streak_seq1=4,
        bias_correction_seq1=0.5,
        max_streak_seq2=3,
        bias_correction_seq2=0.5,
        reward_stim_options=reward_stim_options,
        reward_stim_options_mac=reward_stim_options_mac
    )

    csv_path = "/Users/IrisW/Desktop/testing.csv"
    generator.run(csv_path)
    print("Done")
'''

'''
import random
import pandas as pd
from collections import Counter


class AST_trgen_ver1:
    def __init__(self, sequence_length: int,
                 max_streak_seq1: int, bias_correction_seq1: float,
                 max_streak_seq2: int, bias_correction_seq2: float,
                 reward_stim_options: list, reward_stim_options_mac: list):
        self.sequence_length = sequence_length
        self.max_streak_seq1 = max_streak_seq1
        self.bias_correction_seq1 = bias_correction_seq1
        self.max_streak_seq2 = max_streak_seq2
        self.bias_correction_seq2 = bias_correction_seq2
        self.reward_stim_options = reward_stim_options
        self.reward_stim_options_mac = reward_stim_options_mac
        self.df = None

    def generate_biased_sequence(self, length: int, bias_correction: float) -> list:
        return [1 if random.random() > bias_correction else 0 for _ in range(length)]

    def rearrange_sequence(self, sequence: list, max_streak: int) -> list:
        i = 0
        while i <= len(sequence) - max_streak:
            if all(sequence[i] == sequence[i + j] for j in range(max_streak)):
                swap_idx = next((j for j in range(i + max_streak, len(sequence))
                                 if sequence[j] != sequence[i]), None)
                if swap_idx is not None:
                    sequence[i + max_streak - 1], sequence[swap_idx] = sequence[swap_idx], sequence[i + max_streak - 1]
                else:
                    break
            i += 1
        return sequence

    def generate_sequence(self, length: int, max_streak: int, bias_correction: float) -> list:
        while True:
            seq = self.generate_biased_sequence(length, bias_correction)
            seq = self.rearrange_sequence(seq, max_streak)
            if self.validate_no_long_pattern(seq):
                return seq

    def validate_no_long_pattern(self, sequence: list) -> bool:
        pattern_str = ''.join(['L' if x == 0 else 'R' for x in sequence])
        for i in range(3, len(pattern_str)//2 + 1):
            pattern = pattern_str[:i]
            if pattern * (len(pattern_str) // len(pattern)) == pattern_str[:len(pattern) * (len(pattern_str) // len(pattern))]:
                return False
        return True

    def assign_reward_side(self, sequence: list) -> list:
        return ["Left" if num == 0 else "Right" for num in sequence]

    def choose_reward_stimulus(self) -> str:
        return random.choice(self.reward_stim_options)

    def create_reward_dataframe(self, seq: list, seq2: list, reward_stim: str) -> pd.DataFrame:
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
            reward_stimulus = left if reward in left else right
            other_stimulus = right if reward in left else left
            return (reward_stimulus, other_stimulus) if row["reward_side"] == "Left" else (other_stimulus, reward_stimulus)

        df[["left_stim", "right_stim"]] = df.apply(assign_stimuli, axis=1, result_type="expand")
        df.drop(columns=["selected_pairs"], inplace=True)

        return df

    def validate_bins(self, df: pd.DataFrame) -> bool:
        for i in range(0, len(df), 8):
            bin_df = df.iloc[i:i+8]
            if len(bin_df) < 8:
                break

            # Count pair appearances
            pairs = [(l, r) for l, r in zip(bin_df['left_stim'], bin_df['right_stim'])]
            pair_types = [tuple(sorted([l, r])) for l, r in pairs]
            pair_counts = Counter(pair_types)
            if len(pair_counts) < 2 or min(pair_counts.values()) < 2:
                return False

            # Reward side balance within each pair
            pair_reward_sides = {}
            for l, r, side in zip(bin_df['left_stim'], bin_df['right_stim'], bin_df['reward_side']):
                pair = tuple(sorted([l, r]))
                if pair not in pair_reward_sides:
                    pair_reward_sides[pair] = []
                pair_reward_sides[pair].append(side)

            for sides in pair_reward_sides.values():
                if abs(sides.count("Left") - sides.count("Right")) > 1:
                    return False

            # Avoid long repeating L/R reward patterns
            rwd_pattern = ''.join(['L' if side == 'Left' else 'R' for side in bin_df["reward_side"]])
            if any(rwd_pattern[j:j+3] == rwd_pattern[j+3:j+6] for j in range(len(rwd_pattern)-5)):
                return False

        return True

    def save_dataframe_to_csv(self, file_path: str) -> None:
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
        else:
            print("No DataFrame available to save. Please run the generator first.")

    def run(self, csv_path: str = None) -> None:
        max_attempts = 5000
        for attempt in range(max_attempts):
            seq = self.generate_sequence(self.sequence_length, self.max_streak_seq1, self.bias_correction_seq1)
            seq2 = self.generate_sequence(self.sequence_length, self.max_streak_seq2, self.bias_correction_seq2)
            reward_stim = self.choose_reward_stimulus()
            df = self.create_reward_dataframe(seq, seq2, reward_stim)
            if df is not None and self.validate_bins(df):
                self.df = df
                break
        else:
            raise RuntimeError("Failed to generate a valid sequence within retry limit.")

        print("Final DataFrame:")
        print(self.df)

        if csv_path:
            self.save_dataframe_to_csv(csv_path)


if __name__ == '__main__':
    reward_stim_options = ["Whshred", "Card"]
    reward_stim_options_mac = [
        ["Lemon/Whshred", "Anise/Card"],
        ["Lemon/Card", "Anise/Whshred"]
    ]

    generator = AST_trgen_ver1(
        sequence_length=55,
        max_streak_seq1=4,
        bias_correction_seq1=0.5,
        max_streak_seq2=3,
        bias_correction_seq2=0.5,
        reward_stim_options=reward_stim_options,
        reward_stim_options_mac=reward_stim_options_mac
    )

    csv_path = "/Users/IrisW/Desktop/testing.csv"
    generator.run(csv_path)
    print("Done")
'''

'''
import random
import pandas as pd
from collections import Counter


class AST_trgen_ver1:
    def __init__(self, sequence_length: int,
                 max_streak_seq1: int, bias_correction_seq1: float,
                 max_streak_seq2: int, bias_correction_seq2: float,
                 reward_stim_options: list, reward_stim_options_mac: list):
        self.sequence_length = sequence_length
        self.max_streak_seq1 = max_streak_seq1
        self.bias_correction_seq1 = bias_correction_seq1
        self.max_streak_seq2 = max_streak_seq2
        self.bias_correction_seq2 = bias_correction_seq2
        self.reward_stim_options = reward_stim_options
        self.reward_stim_options_mac = reward_stim_options_mac
        self.df = None

    def choose_reward_stimulus(self) -> str:
        return random.choice(self.reward_stim_options)

    def generate_trial_bin(self, reward_stim: str) -> list:
        max_tries = 1000
        for _ in range(max_tries):
            trials = []
            pair_counts = {0: 0, 1: 0}
            pair_side_counts = {0: {"Left": 0, "Right": 0}, 1: {"Left": 0, "Right": 0}}
            reward_side_sequence = []

            for i in range(8):
                options = []
                for pair_idx in [0, 1]:
                    if pair_counts[pair_idx] >= 6:
                        continue
                    for side in ["Left", "Right"]:
                        if abs(pair_side_counts[pair_idx]["Left"] - pair_side_counts[pair_idx]["Right"]) >= 1 and \
                           pair_side_counts[pair_idx][side] > pair_side_counts[pair_idx]["Left" if side == "Right" else "Right"]:
                            continue
                        options.append((pair_idx, side))

                random.shuffle(options)

                for pair_idx, reward_side in options:
                    # Check streaks on reward side
                    side_val = 0 if reward_side == "Left" else 1
                    if len(reward_side_sequence) >= self.max_streak_seq1 and \
                       all(s == side_val for s in reward_side_sequence[-self.max_streak_seq1:]):
                        continue

                    pair = self.reward_stim_options_mac[pair_idx]
                    reward_stimulus = pair[0] if reward_stim in pair[0] else pair[1]
                    other_stimulus = pair[1] if reward_stim in pair[0] else pair[0]
                    left_stim, right_stim = (reward_stimulus, other_stimulus) if reward_side == "Left" else (other_stimulus, reward_stimulus)

                    trials.append({
                        "reward_side": reward_side,
                        "reward_stim": reward_stim,
                        "left_stim": left_stim,
                        "right_stim": right_stim,
                        "pair_idx": pair_idx
                    })

                    pair_counts[pair_idx] += 1
                    pair_side_counts[pair_idx][reward_side] += 1
                    reward_side_sequence.append(side_val)
                    break
                else:
                    break

            if len(trials) == 8 and all(count >= 2 for count in pair_counts.values()) and \
               all(abs(s["Left"] - s["Right"]) <= 1 for s in pair_side_counts.values()):
                return trials

        return []

    def generate_full_sequence(self, reward_stim: str) -> pd.DataFrame:
        trials = []
        num_bins = self.sequence_length // 8

        for _ in range(num_bins):
            bin_trials = self.generate_trial_bin(reward_stim)
            if not bin_trials:
                return None  # Fail to build one bin
            trials.extend(bin_trials)

        df = pd.DataFrame(trials)
        return df

    def validate_final_sequence(self, df: pd.DataFrame) -> bool:
        reward_pattern = ''.join(['L' if side == 'Left' else 'R' for side in df["reward_side"]])
        for i in range(len(reward_pattern) - 5):
            if reward_pattern[i:i+3] == reward_pattern[i+3:i+6]:
                return False

        reward_seq = [0 if side == "Left" else 1 for side in df["reward_side"]]
        return self.validate_no_long_pattern(reward_seq, self.max_streak_seq1)

    def validate_no_long_pattern(self, sequence: list, max_streak: int) -> bool:
        streak = 1
        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i - 1]:
                streak += 1
                if streak > max_streak:
                    return False
            else:
                streak = 1
        return True

    def save_dataframe_to_csv(self, file_path: str) -> None:
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
        else:
            print("No DataFrame available to save. Please run the generator first.")

    def run(self, csv_path: str = None) -> None:
        max_attempts = 500
        for attempt in range(max_attempts):
            reward_stim = self.choose_reward_stimulus()
            df = self.generate_full_sequence(reward_stim)
            if df is not None and self.validate_final_sequence(df):
                self.df = df
                break
        else:
            raise RuntimeError("Failed to generate a valid sequence within retry limit.")

        print("Final DataFrame:")
        print(self.df)

        if csv_path:
            self.save_dataframe_to_csv(csv_path)


if __name__ == '__main__':
    reward_stim_options = ["Whshred", "Card"]
    reward_stim_options_mac = [
        ["Lemon/Whshred", "Anise/Card"],
        ["Lemon/Card", "Anise/Whshred"]
    ]

    generator = AST_trgen_ver1(
        sequence_length=56,
        max_streak_seq1=4,
        bias_correction_seq1=0.5,
        max_streak_seq2=3,
        bias_correction_seq2=0.5,
        reward_stim_options=reward_stim_options,
        reward_stim_options_mac=reward_stim_options_mac
    )

    csv_path = "/Users/IrisW/Desktop/testing.csv"
    generator.run(csv_path)
    print("Done")
'''
import random
import pandas as pd
from collections import Counter


class AST_trgen_ver1:
    def __init__(self, sequence_length: int,
                 max_streak_seq1: int, bias_correction_seq1: float,
                 max_streak_seq2: int, bias_correction_seq2: float,
                 reward_stim_options: list, reward_stim_options_mac: list):
        self.sequence_length = sequence_length
        self.max_streak_seq1 = max_streak_seq1
        self.bias_correction_seq1 = bias_correction_seq1
        self.max_streak_seq2 = max_streak_seq2
        self.bias_correction_seq2 = bias_correction_seq2
        self.reward_stim_options = reward_stim_options
        self.reward_stim_options_mac = reward_stim_options_mac
        self.df = None

    def choose_reward_stimulus(self) -> str:
        return random.choice(self.reward_stim_options)

    def generate_trial_bin(self, reward_stim: str, global_pair_side_counts) -> list:
        max_tries = 1000
        for _ in range(max_tries):
            trials = []
            pair_counts = {0: 0, 1: 0}
            pair_side_counts = {0: {"Left": 0, "Right": 0}, 1: {"Left": 0, "Right": 0}}
            reward_side_sequence = []

            for i in range(8):
                options = []
                for pair_idx in [0, 1]:
                    if pair_counts[pair_idx] >= 6:
                        continue
                    for side in ["Left", "Right"]:
                        # Target balance globally
                        total = global_pair_side_counts[pair_idx]["Left"] + global_pair_side_counts[pair_idx]["Right"]
                        target = total // 2
                        if global_pair_side_counts[pair_idx][side] > target:
                            continue

                        # Prevent local bin imbalance (±1 max)
                        if abs(pair_side_counts[pair_idx]["Left"] - pair_side_counts[pair_idx]["Right"]) >= 1 and \
                           pair_side_counts[pair_idx][side] > pair_side_counts[pair_idx]["Left" if side == "Right" else "Right"]:
                            continue

                        options.append((pair_idx, side))

                random.shuffle(options)

                for pair_idx, reward_side in options:
                    side_val = 0 if reward_side == "Left" else 1
                    if len(reward_side_sequence) >= self.max_streak_seq1 - 1 and \
                       all(s == side_val for s in reward_side_sequence[-(self.max_streak_seq1 - 1):]):
                        continue

                    pair = self.reward_stim_options_mac[pair_idx]
                    reward_stimulus = pair[0] if reward_stim in pair[0] else pair[1]
                    other_stimulus = pair[1] if reward_stim in pair[0] else pair[0]
                    left_stim, right_stim = (reward_stimulus, other_stimulus) if reward_side == "Left" else (other_stimulus, reward_stimulus)

                    trials.append({
                        "reward_side": reward_side,
                        "reward_stim": reward_stim,
                        "left_stim": left_stim,
                        "right_stim": right_stim,
                        "pair_idx": pair_idx
                    })

                    pair_counts[pair_idx] += 1
                    pair_side_counts[pair_idx][reward_side] += 1
                    global_pair_side_counts[pair_idx][reward_side] += 1
                    reward_side_sequence.append(side_val)
                    break
                else:
                    break

            if len(trials) == 8 and all(count >= 2 for count in pair_counts.values()) and \
               all(abs(s["Left"] - s["Right"]) <= 1 for s in pair_side_counts.values()):
                return trials

        return []

    def generate_full_sequence(self, reward_stim: str) -> pd.DataFrame:
        trials = []
        num_bins = self.sequence_length // 8
        global_pair_side_counts = {0: {"Left": 0, "Right": 0}, 1: {"Left": 0, "Right": 0}}

        for _ in range(num_bins):
            bin_trials = self.generate_trial_bin(reward_stim, global_pair_side_counts)
            if not bin_trials:
                return None  # Fail to build one bin
            trials.extend(bin_trials)

        df = pd.DataFrame(trials)
        return df

    def validate_final_sequence(self, df: pd.DataFrame) -> bool:
        reward_pattern = ''.join(['L' if side == 'Left' else 'R' for side in df["reward_side"]])
        for i in range(len(reward_pattern) - 5):
            if reward_pattern[i:i+3] == reward_pattern[i+3:i+6]:
                return False

        reward_seq = [0 if side == "Left" else 1 for side in df["reward_side"]]
        return self.validate_no_long_pattern(reward_seq, self.max_streak_seq1)

    def validate_no_long_pattern(self, sequence: list, max_streak: int) -> bool:
        streak = 1
        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i - 1]:
                streak += 1
                if streak >= max_streak:
                    return False
            else:
                streak = 1
        return True

    def save_dataframe_to_csv(self, file_path: str) -> None:
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
        else:
            print("No DataFrame available to save. Please run the generator first.")

    def run(self, csv_path: str = None) -> None:
        max_attempts = 500
        for attempt in range(max_attempts):
            reward_stim = self.choose_reward_stimulus()
            df = self.generate_full_sequence(reward_stim)
            if df is not None and self.validate_final_sequence(df):
                self.df = df
                break
        else:
            raise RuntimeError("Failed to generate a valid sequence within retry limit.")

        print("Final DataFrame:")
        print(self.df)

        if csv_path:
            self.save_dataframe_to_csv(csv_path)


if __name__ == '__main__':
    reward_stim_options = ["Whshred", "Card"]
    reward_stim_options_mac = [
        ["Lemon/Whshred", "Anise/Card"],
        ["Lemon/Card", "Anise/Whshred"]
    ]

    generator = AST_trgen_ver1(
        sequence_length=56,
        max_streak_seq1=4,
        bias_correction_seq1=0.5,
        max_streak_seq2=3,
        bias_correction_seq2=0.5,
        reward_stim_options=reward_stim_options,
        reward_stim_options_mac=reward_stim_options_mac
    )

    csv_path = "/Users/IrisW/Desktop/testing.csv"
    generator.run(csv_path)
    print("Done")

