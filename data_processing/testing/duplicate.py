import csv

# Hardcoded file paths
input_file = '/Users/andrewchung/Desktop/PythonCode/Files_Redo.csv'  # Replace with your input file path
output_file = '/Users/andrewchung/Desktop/PythonCode/Files_Redo_1.csv'  # Replace with your desired output file path

def remove_duplicate_filenames(input_file, output_file):
    """
    Remove duplicate filenames from a CSV file and write unique filenames to a new CSV file.

    Args:
    input_file (str): Path to the input CSV file containing filenames.
    output_file (str): Path to the output CSV file where unique filenames will be written.
    """
    # Read the input CSV file
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # Store unique filenames
        unique_filenames = []
        for row in reader:
            # Check if the row is not empty and the filename is not already in the list
            if row and row[0] not in unique_filenames:
                unique_filenames.append(row[0])

    # Write the unique filenames to the output CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for filename in unique_filenames:
            writer.writerow([filename])

    print(f"Duplicate filenames removed. Result saved to {output_file}")

if __name__ == "__main__":
    # Execute the function when the script is run directly
    remove_duplicate_filenames(input_file, output_file)