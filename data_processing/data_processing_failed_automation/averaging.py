import pandas as pd
import os
import csv

# Function to determine if a number is even or odd
def is_even(number):
    return number % 2 == 0

# Function to calculate the average of a list
def calculate_average(values):
    return sum(values) / len(values) if values else 0

def process_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Initialize dictionaries to store the values for each group
    groups = {
        'ProOne_even': {'Left': [], 'Right': [], 'Top': [], 'Bottom': []},
        'ProOne_odd': {'Left': [], 'Right': [], 'Top': [], 'Bottom': []},
        'E8XT_even': {'Left': [], 'Right': [], 'Top': [], 'Bottom': []},
        'E8XT_odd': {'Left': [], 'Right': [], 'Top': [], 'Bottom': []}
    }

    # Process each row in the dataframe
    for index, row in df.iterrows():
        filename = row['Filename']
        parts = filename.split('_')
        model = parts[2]
        number = int(parts[3])
        left = row['Left']
        right = row['Right']
        top = row['Top']
        bottom = row['Bottom']
        
        if 'ProOne' in filename:
            group = 'ProOne_even' if is_even(number) else 'ProOne_odd'
        elif 'E8XT' in filename:
            group = 'E8XT_even' if is_even(number) else 'E8XT_odd'
        else:
            continue  # Skip if not ProOne or E8XT
        
        groups[group]['Left'].append(left)
        groups[group]['Right'].append(right)
        groups[group]['Top'].append(top)
        groups[group]['Bottom'].append(bottom)

    # Calculate the averages for each group
    averages = {}
    for group_name, values in groups.items():
        averages[group_name] = {
            'Left': calculate_average(values['Left']),
            'Right': calculate_average(values['Right']),
            'Top': calculate_average(values['Top']),
            'Bottom': calculate_average(values['Bottom'])
        }

    return averages

def main():
    # Specify the directory containing CSV files
    directory = r'C:\Users\andre\OneDrive\Desktop\SCRG\distance_csv\cleaned'
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(directory, 'processed_results')
    os.makedirs(output_dir, exist_ok=True)

    # Process each CSV file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            print(f"Processing {filename}...")
            
            averages = process_csv(file_path)
            
            # Create output CSV file
            output_file = os.path.join(output_dir, f'processed_{filename}')
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Group', 'Left', 'Right', 'Top', 'Bottom'])
                for group, values in averages.items():
                    writer.writerow([group, values['Left'], values['Right'], values['Top'], values['Bottom']])
            
            print(f"Results saved to {output_file}")

    print("All files processed.")

if __name__ == "__main__":
    main()