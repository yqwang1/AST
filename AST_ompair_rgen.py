# Created by: yeqing wang
# Date: 2025-03-10 09:07:56 
# Description: AST_ompair_rgen, psuedo ramdon generator for odor and material pair.

import random

def generate_and_random_shift_pairs(odors, materials):
    if len(odors) != len(materials):
        raise ValueError("Odor and Material lists must have the same length")

    random.shuffle(odors)  # Shuffle odors randomly
    pairs = list(zip(odors, materials))  # Pair them

    # Generate a random shift value
    shift = random.randint(1, len(pairs) - 1)  # Ensures at least 1 shift
    shifted_pairs = pairs[-shift:] + pairs[:-shift]

    return shifted_pairs


# Example usage:
if __name__ == "__main__":
    odors = ["Rosemary", "Lemon", "Clove", "Nutmeg", "Turmeric", "Anise", "Ginger", "Citronella", "Thyme", "Lavender",
             "Cinnamon", "Vanilla"]
    materials = ["WhBed", "Pipes", "Raffila", "Whshred", "Cotton", "Card", "Cord", "Metal strip", "Ribbon", "Paper",
                 "Felt", "Tissue"]

    random_shifted_pairs = generate_and_random_shift_pairs(odors, materials)

    # Print results
    for odor, material in random_shifted_pairs:
        print(f"Odor: {odor} - Material: {material}")

