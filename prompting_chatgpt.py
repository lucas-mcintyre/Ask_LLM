import os
import pandas as pd
from scipy import spatial  # for calculating vector similarities for search
import tiktoken  # for counting tokens
from ast import literal_eval

from embedding_dataset_openai import get_embedding, convert_to_float64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


# Fonction de similarité
def relatedness_fn(x, y):
    return 1 - spatial.distance.cosine(x, y)

# Fonction de recherche
def strings_ranked_by_relatedness(query, df, threshold=0, top_n=50)-> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    
    query_embedding = get_embedding(query)
    query_embedding = convert_to_float64(query_embedding)

    strings_and_relatednesses = [
        (row["content"], row["page_nb"], row["date"], row["document_name"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[4], reverse=True)

    if threshold > 0: #seuil de pertinence
        strings_and_relatednesses = [(c, p, d, n, r) for c, p, d, n, r in strings_and_relatednesses if r >= threshold]

    if strings_and_relatednesses == []:
        return None
    
    contents, pages, dates, document_names, relatednesses = zip(*strings_and_relatednesses)
    return contents[:top_n], pages[:top_n], dates[:top_n], document_names[:top_n], relatednesses[:top_n]

# Fonction de comptage de tokens
def num_tokens(text: str, model: str ) -> int:
    """Retourne le nombre de token dans un string"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Fonction de génération de prompt
def query_message(query, df, model, token_budget, threshold=0, top_n=50) -> str:
    
    """Retourne le message a fournir au LLM, avec les sources pertinentes tirées de la base de données. """
    
    contents, pages, dates, document_names, relatednesses = strings_ranked_by_relatedness(query, df, threshold, top_n)
    introduction = "Utilisez l'historique de la conversation et les documents ci-dessous pour répondre à la question suivante. Si c'est pertinent, référencez votre réponse en utilisant le titre des documents et la page. Si la réponse est introuvable, écrivez 'Je n'ai pas trouvé de réponse'."
    question = f"\n\nQuestion: {query}"
    message = introduction
    for content, page, date, document_name, relatedness in zip(contents, pages, dates, document_names, relatednesses):
        next_doc = f"\n\nNom du document: {document_name}:\n\nDate: {date}\n\nPage numero: {page}\n\nContenu:{content}" 
        
        #si le model commence par "gpt", on rentre dans la boucle
        if model.startswith("gpt"):
            if ( num_tokens(message + next_doc + question, model=model) > token_budget ):
                break
            else:
                message += next_doc
    return message + question

# Fonction de réponse
def ask_chatgpt(query, df, model, token_budget= 4096 - 500, print_message=False, keep_in_memory=False, threshold=0, top_n=50, history=[]) -> str:
   
    """Répond a une question en utilisant GPT et une base de données de documents vectorisés."""
    
    message = query_message(query, df, model, token_budget, threshold, top_n)
    if print_message:
        print(message)
        
    messages = [{"role": "system", "content": "Tu répond à un travailleur à propos des documents de son entreprise."}] 
    
    if len(history) > 0: #TODO
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    
    response = client.chat.completions.create(model=model, messages=messages, temperature=0)
    response_message = response.choices[0].message.content

    if keep_in_memory: #TODO
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response_message})
        
    return response_message

def clear_memory(previous_messages):
    #TODO
    return "memory cleared"


MODEL = "gpt-4" # "gpt-4-0125-preview" or "gpt-4" or "gpt-3.5-turbo-0125" or "gpt-3.5-turbo" or others
HISTORY = []

if __name__ == "__main__":

    df = pd.read_csv("embedded_chunks_dataset.csv", sep=';', encoding='utf-8-sig', converters = {'embedding': literal_eval}) 

    query = "fait moi un résumé du contrat avec hervé thermique ?"
    
    response = ask_chatgpt(query, df, MODEL, token_budget=4096 - 500, print_message=True, keep_in_memory=False, threshold=0, top_n=50, history=HISTORY)
    print(response)
    
    