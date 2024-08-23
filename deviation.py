import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
import os

def load_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        
        required_columns = ['timestamp', 'pressure', 'temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
        
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        df['time_diff'] = df['timestamp'].diff()
        
        return df
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None

def calculate_std_devs(df):
    std_devs = {}
    for column in ['pressure', 'temperature', 'time_diff']:
        if column in df.columns:
            std_devs[f'{column}_std'] = df[column].dropna().std()
        else:
            print(f"Warning: '{column}' column not found in the DataFrame.")
    return std_devs

def create_comparison_graph(data, labels, metric, title):
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(x, data, width)

    ax.set_ylabel(f'Standard Deviation of {metric}')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.6f}',
                ha='center', va='bottom', rotation=0)

    plt.tight_layout()
    plt.savefig(f'{metric.lower().replace(" ", "_")}_comparison.png')
    plt.close()

def print_summary_table(std_devs, labels):
    table_data = []
    headers = ['File', 'Pressure StdDev', 'Temperature StdDev', 'Time Steps StdDev']
    
    for label, std_dev in zip(labels, std_devs):
        row = [
            label,
            f"{std_dev.get('pressure_std', 'N/A'):.6f}",
            f"{std_dev.get('temperature_std', 'N/A'):.6f}",
            f"{std_dev.get('time_diff_std', 'N/A'):.6f}"
        ]
        table_data.append(row)
    
    print("\nSummary of Standard Deviations:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main(file_paths):
    if len(file_paths) < 2:
        print("Error: Please provide at least two CSV file paths.")
        return

    dataframes = []
    labels = []

    for file_path in file_paths:
        df = load_and_process_csv(file_path)
        if df is not None:
            dataframes.append(df)
            labels.append(os.path.basename(file_path))  # Use the file name as the label

    if len(dataframes) < 2:
        print("Error: Unable to process at least two CSV files. Please check the file formats and paths.")
        return

    std_devs = [calculate_std_devs(df) for df in dataframes]

    metrics = [('Pressure', 'pressure_std'), ('Temperature', 'temperature_std'), ('Time Steps', 'time_diff_std')]
    for metric_name, metric_key in metrics:
        data = []
        valid_labels = []
        for label, std_dev in zip(labels, std_devs):
            if metric_key in std_dev:
                data.append(std_dev[metric_key])
                valid_labels.append(label)
            else:
                print(f"Warning: '{metric_key}' not found for file {label}. Skipping this file for {metric_name} comparison.")
        
        if data:
            create_comparison_graph(data, valid_labels, metric_name, f'Comparison of {metric_name} Standard Deviation')
        else:
            print(f"Error: No data available for {metric_name} comparison. Skipping this graph.")

    print("Graphs have been generated and saved.")
    
    # Print summary table
    print_summary_table(std_devs, labels)


if __name__ == "__main__":
    # Specify your file paths here
    file_paths = [
        'C:/Users/Plaid/Downloads/256.csv',
        'C:/Users/Plaid/Downloads/512.csv',
        'C:/Users/Plaid/Downloads/1024.csv',
        'C:/Users/Plaid/Downloads/2048.csv',
        'C:/Users/Plaid/Downloads/4096.csv',
    ]

    main(file_paths)
