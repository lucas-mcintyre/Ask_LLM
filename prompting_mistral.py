import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
from ast import literal_eval
from embedding_dataset_openai import get_embedding, convert_to_float64
from prompting_chatgpt import query_message 


def test_installation():
    print(torch.__version__)
    if torch.cuda.is_available():
        print("Cuda is available")
    else:
        print("Cuda is not available")

def model_initialization():
    # model_id = "mistralai/Mistral-7B-v0.1"
    model_id = "amazon/MistralLite"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    return model, tokenizer

def ask_mistral(query, df, model, token_budget, print_message=True, keep_in_memory=False, threshold=0, top_n=50, history=[]):
    """
    Ask Mistral a question and return the response.

    Returns:
        str: The response from Mistral.
    """
    
    message = query_message(query, df, MODEL, token_budget, threshold, top_n)
    if print_message:  
        print(message)
    
    
    inputs = tokenizer(message, return_tensors="pt")
    print("Models is generation")

    outputs = model.generate(**inputs, max_length=token_budget, do_sample=True, top_k=50, top_p=0.95, temperature=0.7, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)    
    return response


MODEL = "MistralLite"

if __name__ == "__main__":

    try:
        model = AutoModelForCausalLM.from_pretrained("./saved_model")
        tokenizer = AutoTokenizer.from_pretrained("./saved_model")
        print("Model loaded from local directory.")
    except:
        # If not found locally, load from Hugging Face model hub and save locally
        model, tokenizer = model_initialization()
        model.save_pretrained("./saved_model")
        tokenizer.save_pretrained("./saved_model")
        print("Model downloaded from Hugging Face and saved locally.")

    df = pd.read_csv("embedded_chunks_dataset.csv", sep=';', encoding='utf-8-sig', converters = {'embedding': literal_eval}) 

    query = "fait moi un résumé du contrat avec hervé thermique ?"
    
    test_installation()

    response = ask_mistral(query, df, model, token_budget=4096 - 500, print_message=True, keep_in_memory=False, threshold=0, top_n=50)
    print(response)
    
