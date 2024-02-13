import csv
import os
import zipfile
import pandas as pd
import ast


def helper_tables_to_text(file_path) -> str:
    """
    Takes a table CSV file and turns it into text that can be added to dataset.

    Parameters:
    - file_path: The path to the CSV file.

    Returns:
    - A string representing the formatted data suitable for a text prompt.
    """

    # Initialize a list to hold formatted text
    formatted_text_list = []

    # Open the CSV file for reading
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        # Create a CSV reader object
        reader = csv.reader(csv_file)

        # Extract headers
        headers = next(reader, None)

        if headers:
            # Create a header line if headers are present
            header_line = " | ".join(headers)
            formatted_text_list.append(header_line)

        # Iterate over the rows in the CSV file
        for row in reader:
            # Create a formatted string for each row
            row_text = " | ".join(row)
            formatted_text_list.append(row_text)

    # Join all formatted text into a single string with line breaks
    formatted_text = "\n".join(formatted_text_list)

    return formatted_text


def unzip_folder(output_zip_file: str, output_data_folder: str):
    # Open and extract all files in the ZIP file
    with zipfile.ZipFile(output_zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_data_folder)
    os.remove(output_zip_file)


def concatenate_lists_in_csv(input_file, output_file):
    df = pd.read_csv(input_file, sep=";", header=None)

    # Initialize variables to store concatenated rows
    concatenated_rows = []
    is_list = False

    # Iterate through DataFrame rows
    for index, row in df.iterrows():
        # If the second column contains "-", concatenate with the previous row
        #TODO : add check : prev row
        if row[1].startswith("-"):
            concatenated_rows[-1][1] += " " + row[1]
            is_list = True
        elif is_list:
            concatenated_rows[-1][1] += " " + row[1]
            is_list = False
        else:
            concatenated_rows.append(row)

    # Create a new DataFrame from the concatenated rows
    concatenated_df = pd.DataFrame(concatenated_rows)
    # Write the new DataFrame to a new CSV file
    concatenated_df.to_csv(output_file, sep=";", header=False, index=False)

def convert_string_to_list(string):
    try:
        return ast.literal_eval(string)
    except ValueError:
        return string  



if __name__ == "__main__":
    csv_file_path = "pdf_extract_output/2024 Condition particuliére - Infogérance - iot valley (1) copie.csv"
    output_file = "pdf_extract_output/test_concatenated.csv"
    concatenate_lists_in_csv(csv_file_path, output_file)