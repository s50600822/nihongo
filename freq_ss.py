import os
from collections import Counter

def get_substrings(text):
    """Generate all possible substrings of a given text."""
    substrings = []
    length = len(text)
    for start in range(length):
        for end in range(start + 1, length + 1):
            substrings.append(text[start:end])
    return substrings

def find_top_n_frequent_substrings(directory_path, top_n=10):
    """Find the top N most frequent substrings from all files in a directory."""
    counter = Counter()

    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        
        if os.path.isfile(filepath):
            # Read the content of the file
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
                # Generate substrings and update frequency counter
                substrings = get_substrings(content)
                counter.update(substrings)
    
    # Find the top N frequent substrings
    most_common_substrings = counter.most_common(top_n)
    return most_common_substrings

# Directory containing files
directory_path = './lyrics'

top_n = 100
top_substrings = find_top_n_frequent_substrings(directory_path, top_n)
if top_substrings:
    for substring, frequency in top_substrings:
        print(f"'{substring}' - Frequency: {frequency}")
else:
    print("No substrings found.")
