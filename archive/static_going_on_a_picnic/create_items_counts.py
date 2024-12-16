import json
from collections import defaultdict
from itertools import combinations

# Load items from the Open Images dataset
with open('open_images_combined_items.json', 'r') as file:
    items = json.load(file)

# Initialize dictionaries for counting occurrences
l1_counts = defaultdict(int)
l2_counts = defaultdict(int)
l3_counts = defaultdict(int)

# Count occurrences for individual tags (L1)
for item, tags in items.items():
    for tag in tags:
        l1_counts[(tag,)] += 1

# Count occurrences for pairs of tags (L2)
for item, tags in items.items():
    for pair in combinations(tags, 2):
        l2_counts[tuple(sorted(pair))] += 1

# Count occurrences for triplets of tags (L3)
for item, tags in items.items():
    for triplet in combinations(tags, 3):
        l3_counts[tuple(sorted(triplet))] += 1

# Convert tuple keys to JSON-compatible strings
l1_counts_str_keys = {str(list(key)): value for key, value in l1_counts.items()}
l2_counts_str_keys = {str(list(key)): value for key, value in l2_counts.items()}
l3_counts_str_keys = {str(list(key)): value for key, value in l3_counts.items()}

# Sort by decreasing count
l1_counts_str_keys = dict(sorted(l1_counts_str_keys.items(), key=lambda item: item[1], reverse=True))
l2_counts_str_keys = dict(sorted(l2_counts_str_keys.items(), key=lambda item: item[1], reverse=True))
l3_counts_str_keys = dict(sorted(l3_counts_str_keys.items(), key=lambda item: item[1], reverse=True))

# Save counts to JSON files
with open('l1_individual_counts.json', 'w') as outfile:
    json.dump(l1_counts_str_keys, outfile, indent=4)

with open('l2_pairs_counts.json', 'w') as outfile:
    json.dump(l2_counts_str_keys, outfile, indent=4)

with open('l3_triplets_counts.json', 'w') as outfile:
    json.dump(l3_counts_str_keys, outfile, indent=4)

print("Analysis completed. Counts saved to JSON files with JSON-compatible keys.")
