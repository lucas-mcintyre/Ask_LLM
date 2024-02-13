import os
import pandas as pd

from openai import OpenAI
from dotenv import load_dotenv

from scipy import spatial  # for calculating vector similarities for search


load_dotenv()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def get_embedding(text):
    """
    Get the embedding of a given text using the OpenAI API.

    Args:
        text (str): The input text.

    Returns:
        list: The embedding of the input text.
    """
    if type(text) == str:
        text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding

def convert_to_float64(lst) -> list:
    return [float(x) for x in lst]


EMBEDDING_MODEL = "text-embedding-3-small"  # "text-embedding-3-small" or "text-embedding-3-large"
data_output_folder = os.environ.get('OUTPUT_FOLDER_PATH')

if __name__ == "__main__":
    
    df = pd.read_csv(os.path.join(data_output_folder, "chunks_dataset.csv"), sep=';', encoding='utf-8-sig') 
    list_embeddings = []
    for row in df.iterrows():
        text = f"Nom du document: {row[1]['document_name'] }\n\nDate: {row[1]['date']}\n\nPage numero: {row[1]['page_nb']}\n\nContenu:{row[1]['content']}"
        embedded_text = convert_to_float64(get_embedding(text))
        list_embeddings.append(embedded_text)

    df['embedding'] = list_embeddings 
    df.to_csv("embedded_chunks_dataset.csv", index=False, sep=';', encoding='utf-8-sig') 
    

