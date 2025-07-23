import pandas as pd
import numpy as np
import os

# MAY NEED TO CHANGE THE DIRECTORY PATH
DIRECTORY = r"C:\Users\andre\OneDrive\Desktop\SCRG\distance_csv"

def create_range(value):
    return (value * 0.8, value * 1.2)

ranges = {
    'ProOne_even': {
        'Left': create_range(107.5),
        'Right': create_range(172.55),
        'Top': create_range(112.48),
        'Bottom': create_range(97.475)
    },
    'ProOne_odd': {
        'Left': create_range(133.35),
        'Right': create_range(187.37),
        'Top': create_range(120.79),
        'Bottom': create_range(119.7)
    },
    'E8XT_even': {
        'Left': create_range(73.67),
        'Right': create_range(66.97),
        'Top': create_range(66.5),
        'Bottom': create_range(39.03)
    },
    'E8XT_odd': {
        'Left': create_range(75.51),
        'Right': create_range(71.01),
        'Top': create_range(79.24),
        'Bottom': create_range(30.59)
    }
}

def categorize_row(filename):
    parts = filename.split('_')
    if len(parts) < 4:
        return 'Unknown'
    
    camera_type = parts[2]
    number = parts[3]
    
    if camera_type == 'E8XT':
        if number.isdigit():
            return 'E8XT_even' if int(number) % 2 == 0 else 'E8XT_odd'
        else:
            return 'E8XT_unknown'
    elif camera_type == 'ProOne':
        if number.isdigit():
            return 'ProOne_even' if int(number) % 2 == 0 else 'ProOne_odd'
        else:
            return 'ProOne_unknown'
    else:
        return 'Unknown'

def is_within_range(row, category):
    if category not in ranges:
        return False
    for col in ['Left', 'Right', 'Top', 'Bottom']:
        if not ranges[category][col][0] <= row[col] <= ranges[category][col][1]:
            return False
    return True

def remove_outliers_iqr(df, columns):
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df

def process_file(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Categorize each row
        df['Category'] = df['Filename'].apply(categorize_row)

        # Filter based on expected ranges
        df['Within_Range'] = df.apply(lambda row: is_within_range(row, row['Category']), axis=1)

        # Apply IQR method on the data within expected ranges
        df_in_range = df[df['Within_Range']]
        columns_to_check = ['Left', 'Right', 'Top', 'Bottom']
        df_cleaned = remove_outliers_iqr(df_in_range, columns_to_check)

        # Print results
        print(f"\nProcessing: {os.path.basename(file_path)}")
        print(f"Rows in original dataset: {len(df)}")
        print(f"Rows within expected ranges: {len(df_in_range)}")
        print(f"Rows in final cleaned dataset: {len(df_cleaned)}")
        print(f"Rows removed: {len(df) - len(df_cleaned)}")

        return df_cleaned
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None

def main():
    # Create a 'cleaned' subdirectory if it doesn't exist
    cleaned_dir = os.path.join(DIRECTORY, 'cleaned')
    os.makedirs(cleaned_dir, exist_ok=True)

    # Process all CSV files in the directory
    for filename in os.listdir(DIRECTORY):
        if filename.endswith('.csv'):
            file_path = os.path.join(DIRECTORY, filename)
            cleaned_df = process_file(file_path)
            
            if cleaned_df is not None:
                # Save the cleaned dataset
                cleaned_file_path = os.path.join(cleaned_dir, f'cleaned_{filename}')
                cleaned_df.to_csv(cleaned_file_path, index=False)
                print(f"Cleaned data saved to: {cleaned_file_path}")

if __name__ == "__main__":
    main()