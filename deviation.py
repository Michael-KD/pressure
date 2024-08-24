import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            timestamp = float(row[0]) if row[0] else None
            pressure = float(row[1]) if row[1] else None
            if timestamp is not None and pressure is not None:
                data.append((timestamp, pressure))
    return data

def plot_data(data, ax, title):
    timestamps, pressures = zip(*data)
    relative_times = [(t - timestamps[0]) / 1000 for t in timestamps]  # Convert to seconds
    ax.plot(relative_times, pressures)
    
    # Calculate standard deviation
    std_dev = np.std(pressures)
    
    ax.set_title(f"{title}\n({len(data)/10} hz, σ = {std_dev:.4f} mbar)")
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Pressure (mbar)')
    ax.ticklabel_format(useOffset=False, style='plain')

def main():
    folder_path = 'ten_sec'
    file_order = ['256.csv', '512.csv', '1024.csv', '2048.csv', '4096.csv']
    csv_files = [f for f in file_order if f in os.listdir(folder_path)]
    
    fig, axs = plt.subplots(len(csv_files), 1, figsize=(10, 5*len(csv_files)), sharex=True)
    if len(csv_files) == 1:
        axs = [axs]
    
    all_pressures = []
    for i, csv_file in enumerate(csv_files):
        file_path = os.path.join(folder_path, csv_file)
        data = read_csv(file_path)
        plot_data(data, axs[i], f'Pressure vs Time - {csv_file}')
        all_pressures.extend([p for _, p in data])
    
    # Set uniform y-axis limits
    y_min, y_max = min(all_pressures), max(all_pressures)
    y_range = y_max - y_min
    y_padding = y_range * 0.1  # Add 10% padding
    for ax in axs:
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
    
    plt.tight_layout()
    plt.savefig('pressure_plots.png')
    print("Plots saved as 'pressure_plots.png'")

if __name__ == "__main__":
    main()




# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# from tabulate import tabulate
# import os

# def load_and_process_csv(file_path):
#     try:
#         df = pd.read_csv(file_path)
        
#         required_columns = ['timestamp', 'pressure', 'temperature']
#         missing_columns = [col for col in required_columns if col not in df.columns]
#         if missing_columns:
#             raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
        
#         df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
#         df['time_diff'] = df['timestamp'].diff()
        
#         return df
#     except Exception as e:
#         print(f"Error processing file {file_path}: {str(e)}")
#         return None

# def calculate_std_devs(df):
#     std_devs = {}
#     for column in ['pressure', 'temperature', 'time_diff']:
#         if column in df.columns:
#             std_devs[f'{column}_std'] = df[column].dropna().std()
#         else:
#             print(f"Warning: '{column}' column not found in the DataFrame.")
#     return std_devs

# def create_comparison_graph(data, labels, metric, title):
#     x = np.arange(len(labels))
#     width = 0.35

#     fig, ax = plt.subplots(figsize=(12, 6))
#     bars = ax.bar(x, data, width)

#     ax.set_ylabel(f'Standard Deviation of {metric}')
#     ax.set_title(title)
#     ax.set_xticks(x)
#     ax.set_xticklabels(labels, rotation=45, ha='right')

#     # Add value labels on top of each bar
#     for bar in bars:
#         height = bar.get_height()
#         ax.text(bar.get_x() + bar.get_width()/2., height,
#                 f'{height:.6f}',
#                 ha='center', va='bottom', rotation=0)

#     plt.tight_layout()
#     plt.savefig(f'{metric.lower().replace(" ", "_")}_comparison.png')
#     plt.close()

# def print_summary_table(std_devs, labels):
#     table_data = []
#     headers = ['File', 'Pressure StdDev', 'Temperature StdDev', 'Time Steps StdDev']
    
#     for label, std_dev in zip(labels, std_devs):
#         row = [
#             label,
#             f"{std_dev.get('pressure_std', 'N/A'):.6f}",
#             f"{std_dev.get('temperature_std', 'N/A'):.6f}",
#             f"{std_dev.get('time_diff_std', 'N/A'):.6f}"
#         ]
#         table_data.append(row)
    
#     print("\nSummary of Standard Deviations:")
#     print(tabulate(table_data, headers=headers, tablefmt="grid"))

# def main(file_paths):
#     if len(file_paths) < 2:
#         print("Error: Please provide at least two CSV file paths.")
#         return

#     dataframes = []
#     labels = []

#     for file_path in file_paths:
#         df = load_and_process_csv(file_path)
#         if df is not None:
#             dataframes.append(df)
#             labels.append(os.path.basename(file_path))  # Use the file name as the label

#     if len(dataframes) < 2:
#         print("Error: Unable to process at least two CSV files. Please check the file formats and paths.")
#         return

#     std_devs = [calculate_std_devs(df) for df in dataframes]

#     metrics = [('Pressure', 'pressure_std'), ('Temperature', 'temperature_std'), ('Time Steps', 'time_diff_std')]
#     for metric_name, metric_key in metrics:
#         data = []
#         valid_labels = []
#         for label, std_dev in zip(labels, std_devs):
#             if metric_key in std_dev:
#                 data.append(std_dev[metric_key])
#                 valid_labels.append(label)
#             else:
#                 print(f"Warning: '{metric_key}' not found for file {label}. Skipping this file for {metric_name} comparison.")
        
#         if data:
#             create_comparison_graph(data, valid_labels, metric_name, f'Comparison of {metric_name} Standard Deviation')
#         else:
#             print(f"Error: No data available for {metric_name} comparison. Skipping this graph.")

#     print("Graphs have been generated and saved.")
    
#     # Print summary table
#     print_summary_table(std_devs, labels)


# if __name__ == "__main__":
#     # Specify your file paths here
#     file_paths = [
#         'C:/Users/Plaid/Downloads/256.csv',
#         'C:/Users/Plaid/Downloads/512.csv',
#         'C:/Users/Plaid/Downloads/1024.csv',
#         'C:/Users/Plaid/Downloads/2048.csv',
#         'C:/Users/Plaid/Downloads/4096.csv',
#     ]

#     main(file_paths)
