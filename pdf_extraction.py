from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.table_structure_type import TableStructureType
import os
import json
import csv
from dotenv import load_dotenv

load_dotenv()


def create_credentials() -> ExecutionContext:
    """
    Create and return an execution context using environment variables.

    Returns:
        ExecutionContext: An execution context for Adobe PDF services.
    """
    client_id = os.environ.get('ADOBE_CLIENT_ID')
    client_secret = os.environ.get('ADOBE_CLIENT_SECRET')

    credentials = Credentials.service_principal_credentials_builder() \
        .with_client_id(client_id) \
        .with_client_secret(client_secret) \
        .build()

    return ExecutionContext.create(credentials)


def extract_data(input_pdf: str, execution_context: ExecutionContext, output_zip_file: str) -> None:
    """
    Extract text and tables from a given PDF and save them as a ZIP file.

    Args:
        input_pdf (str): Path to the input PDF file.
        execution_context (ExecutionContext): Adobe PDF services execution context.
    """
    # Create a new PDF extraction operation
    extract_pdf_operation = ExtractPDFOperation.create_new()

    # Create a FileRef instance from the local PDF file
    source = FileRef.create_from_local_file(input_pdf)
    extract_pdf_operation.set_input(source)

    # Configure the operation to extract only text
    extract_pdf_options = ExtractPDFOptions.builder() \
        .with_element_to_extract(ExtractElementType.TEXT) \
        .with_element_to_extract(ExtractElementType.TABLES) \
        .with_table_structure_format(TableStructureType.CSV) \
        .build()
    extract_pdf_operation.set_options(extract_pdf_options)

    # Execute the operation and save the result as a ZIP file
    result = extract_pdf_operation.execute(execution_context)
    result.save_as(output_zip_file)


def get_readable_text_from_json(structuredData_path: str, text_output_csv: str):
    """
  Take the json obtained from the pdf extraction and turn it into a readable csv
  """
    with open(structuredData_path) as f:
        data = json.load(f)
    csv_data = []

    for element in data["elements"]:
        if 'Page' in element and 'Text' in element:
            csv_data.append({
                'page_nb': element['Page'],
                'content': element['Text']
            })

    with open(text_output_csv, 'w', newline='', encoding="utf-8-sig") as csvfile:
        fieldnames = ['page_nb', 'content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)


