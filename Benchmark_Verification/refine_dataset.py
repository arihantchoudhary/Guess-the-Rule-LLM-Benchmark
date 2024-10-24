import pandas as pd
import argparse
import pdb
import ast

# Set up argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(description="Update dataset based on inconsistent results.")
    parser.add_argument('--inconsistent_results_path', type=str, default='./demo_rule/inconsistent_results.csv', help='Path to inconsistent results CSV file')
    parser.add_argument('--dataset_path', type=str, default='./demo_rule/dataset.txt', help='Path to dataset CSV/TXT file')
    parser.add_argument('--output_path', type=str, default='./demo_rule/refine_dataset.txt', help='Path to save the updated dataset CSV file')
    return parser.parse_args()

# Function to update the dataset based on inconsistent results
def update_dataset(dataset, inconsistent_dict):
    updated_dataset = dataset.copy()
    for idx, row in inconsistent_dict.iterrows():
        refine_list = ast.literal_eval(row['Item Details'])
        updated_dataset.loc[row['Index'], 0], updated_dataset.loc[row['Index'], 1] = refine_list[0], refine_list[1]
    return updated_dataset

# Main function
def main():
    # Parse arguments
    args = parse_arguments()

    # Load the CSV files
    inconsistent_results = pd.read_csv(args.inconsistent_results_path, sep=',')
    dataset = pd.read_csv(args.dataset_path, header=None)

    # Convert inconsistent_results to a dictionary for easier lookup

    # Update the dataset
    updated_dataset = update_dataset(dataset, inconsistent_results)

    # Save the updated dataset to a new CSV file
    updated_dataset.to_csv(args.output_path, index=False, header=False)

    print(f"Updated dataset saved to {args.output_path}")

if __name__ == "__main__":
    main()
