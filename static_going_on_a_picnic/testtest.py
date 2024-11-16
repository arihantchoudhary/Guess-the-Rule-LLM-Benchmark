import pandas as pd

filename = "experiment_agg_11_13_2024"
exp_result = pd.read_csv(f'{filename}.csv')
# Model	Difficulty	Max Turns	Win	Turns Taken	Duration (s)	Total Examples Available	Positive Examples Shown	Negative Examples Shown
cols_for_analysis = ['Model','Difficulty', 'Max Turns', 'Turns Taken', 'Duration (s)', 'Total Examples Available', 'Positive Examples Shown', 'Negative Examples Shown']
cols_for_grouping = ['Model', 'Difficulty', 'Max Turns']
mean_results = exp_result[cols_for_analysis].groupby(cols_for_grouping).agg({'Win': 'sum', 'Turns Taken': 'mean', 'Duration (s)': 'mean', 'Total Examples Available': 'mean', 'Positive Examples Shown': 'mean', 'Negative Examples Shown': 'mean'})

mean_results.to_csv(f"{filename}_agg.csv", index=True)
