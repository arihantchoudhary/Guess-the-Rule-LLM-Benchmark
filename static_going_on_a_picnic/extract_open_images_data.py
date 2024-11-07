import pandas as pd
import json
import logging
from collections import defaultdict
import os
from concurrent.futures import ProcessPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load hierarchy data to map each label to all parent labels
def load_label_hierarchy(filepath):
    with open(filepath, 'r') as f:
        hierarchy = json.load(f)

    label_parents = defaultdict(list)

    def add_parents(node, parent_labels):
        label = node["LabelName"]
        label_parents[label].extend(parent_labels)

        if "Subcategory" in node:
            for child in node["Subcategory"]:
                add_parents(child, parent_labels + [label])

    add_parents(hierarchy, [])
    return label_parents

def process_chunk(chunk, label_to_name, label_parents):
    chunk_data = defaultdict(set)
    unique_tags = set()

    for _, row in chunk.iterrows():
        label_name = row["LabelName"]
        confidence = row["Confidence"]

        if confidence == 1:  # Only confirmed labels
            label_display_name = label_to_name.get(label_name)
            if label_display_name:
                parent_labels = label_parents.get(label_name, [])
                for parent_label in parent_labels:
                    parent_display_name = label_to_name.get(parent_label)
                    if parent_display_name and parent_display_name != label_display_name:
                        chunk_data[label_display_name].add(parent_display_name)
                        unique_tags.add(parent_display_name)

    return chunk_data, unique_tags

def process_annotations_in_parallel(annotations_path, label_to_name, label_parents, chunk_size=50000):
    annotations_iter = pd.read_csv(annotations_path, chunksize=chunk_size)
    total_rows = sum(1 for _ in open(annotations_path)) - 1  # Exclude header
    total_chunks = (total_rows // chunk_size) + 1
    logging.info(f"Processing {total_rows} rows in {total_chunks} chunks...")

    combined_data = defaultdict(set)
    all_unique_tags = set()

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_chunk, chunk, label_to_name, label_parents) for chunk in annotations_iter]
        for idx, future in enumerate(futures):
            chunk_data, unique_tags = future.result()
            # Merge chunk data
            for item, tags in chunk_data.items():
                combined_data[item].update(tags)
            all_unique_tags.update(unique_tags)

            logging.info(f"Processed chunk {idx + 1}/{total_chunks}")

    return combined_data, all_unique_tags

def main():
    label_hierarchy_path = "bbox_labels_600_hierarchy.json"
    label_parents = load_label_hierarchy(label_hierarchy_path)

    class_descriptions_path = "class-descriptions-boxable.csv"
    class_descriptions = pd.read_csv(class_descriptions_path, header=None, names=["LabelName", "DisplayName"])
    label_to_name = dict(zip(class_descriptions["LabelName"], class_descriptions["DisplayName"].str.lower()))

    annotations_path = "train-annotations-human-imagelabels.csv"
    combined_data, all_unique_tags = process_annotations_in_parallel(annotations_path, label_to_name, label_parents)

    # Write the final combined data and unique tags to JSON
    with open("open_images_combined_items.json", "w") as f:
        json.dump({key: sorted(list(values)) for key, values in combined_data.items()}, f, indent=4)
    logging.info("Combined data saved to open_images_combined_items.json.")

    with open("open_images_unique_tags.json", "w") as f:
        json.dump(sorted(list(all_unique_tags)), f, indent=4)
    logging.info("Unique tags saved to open_images_unique_tags.json.")

# Ensure main() only runs in the main process
if __name__ == '__main__':
    main()
