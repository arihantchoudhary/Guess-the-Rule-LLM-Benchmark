# processing_results.py

import os
import json
import csv

# Directory containing your JSON log files
script_dir = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(script_dir, 'logs/model_v_itself')
actual_log_directory = os.path.join(script_dir, 'logs')

# Output CSV file path
output_csv = os.path.join(actual_log_directory, "model_v_itself_final_results.csv")

# Collect all JSON files in the directory
json_files = [f for f in os.listdir(log_directory) if f.endswith(".json")]

all_metrics = []

for json_file in json_files:
    file_path = os.path.join(log_directory, json_file)
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Based on your example, the top-level keys in `data` are the metrics.
    # If `conversation` is present, convert it to a string before writing to CSV.
    if "conversation" in data and isinstance(data["conversation"], list):
        data["conversation"] = json.dumps(data["conversation"])

    # Now 'data' itself represents the metrics dictionary.
    all_metrics.append(data)

if not all_metrics:
    print("No metrics found in any JSON files.")
    exit(0)

# Extract the field names from the first metrics dict
fieldnames = list(all_metrics[0].keys())

# Write all metrics to a CSV file
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for m in all_metrics:
        writer.writerow(m)

print(f"Combined metrics CSV has been created at {output_csv}")