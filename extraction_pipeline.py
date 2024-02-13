import os
import csv
import pandas as pd
from pdf_extraction import create_credentials, extract_data, get_readable_text_from_json
from utils import unzip_folder, concatenate_lists_in_csv, helper_tables_to_text


def main_task():
    execution_context = create_credentials()

    input_folder_path = os.environ.get('PDF_INPUT_FOLDER_PATH')
    output_folder_path = os.environ.get('OUTPUT_FOLDER_PATH')
    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Iterate on all inputs pdf
    final_df_all_inputs = pd.DataFrame(columns=['page_nb', 'content'])
    for input_file_name in os.listdir(input_folder_path):
        if input_file_name.endswith('.pdf'):  # Check if the file is a PDF
            input_pdf_path = os.path.join(input_folder_path, input_file_name)
            output_base_name = input_file_name.split(".")[0]

            # Save all the related files in a folder with the same name as the pdf
            data_output_folder = os.path.join(output_folder_path, output_base_name)

            if data_output_folder in os.listdir(output_folder_path):
                print(f"Data already extracted from {input_pdf_path}")
            else:
                # Use Adobe api to extract information from the pdf
                print("---------------------------------")
                print(f"Extracting data from {input_pdf_path}")
                extract_data(input_pdf_path, execution_context, data_output_folder + ".zip")
                unzip_folder(data_output_folder + ".zip", data_output_folder)

                # Get the text from the json file and save it in a csv
                readable_text_csv = os.path.join(data_output_folder, "extracted_text.csv")
                json_path = os.path.join(data_output_folder, "structuredData.json")
                get_readable_text_from_json(json_path, readable_text_csv)
                print("Readable csv texts obtained")

                # Text cleaning : Concatenate the lists in the csv to have better chunks of text
                concatenate_lists_in_csv(readable_text_csv, os.path.join(data_output_folder, "cleaned_text.csv"))
                print("Concatenated csv texts obtained")

                # Tables cleaning : Convert the tables to strings to add them to the csv
                tables_list = []
                for table_file in os.listdir(os.path.join(data_output_folder, "tables")):
                    if table_file.endswith('.csv'):
                        table_path = os.path.join(data_output_folder, "tables", table_file)
                        table_str = helper_tables_to_text(table_path)
                        tables_list.append(table_str)
                header = ["content"]
                with open(os.path.join(data_output_folder, 'tables_str.csv'), 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=';')
                    csv_writer.writerow(header)
                    for item in tables_list:
                        csv_writer.writerow([item])
                print("Tables csv texts obtained")

                # Concatenate the tables csv with the cleaned text csv
                df1 = pd.read_csv(os.path.join(data_output_folder, 'tables_str.csv'), delimiter=';')
                df2 = pd.read_csv(os.path.join(data_output_folder, "cleaned_text.csv"), delimiter=';')
                # Set 'page_nb' to empty for rows from df2
                df1['page_nb'] = ''
                concatenated_df = pd.concat([df1, df2], ignore_index=True)
                concatenated_df.to_csv(os.path.join(data_output_folder, 'final.csv'), index=False, sep=';', encoding='utf-8-sig')
                print(f"Data extracted from {input_pdf_path} and saved in final.csv")
                print("\n")

                #concat to obtain one df with all docs
                final_df_all_inputs = pd.concat([final_df_all_inputs, concatenated_df], ignore_index=True)
    final_df_all_inputs.to_csv(os.path.join(output_folder_path, 'text_dataset_all_inputs.csv'), index=False, sep=';', encoding='utf-8-sig')
    print("FINISH")


if __name__ == "__main__":
    main_task()
