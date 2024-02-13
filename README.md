# Input-tuning pour LLM personnalisé

Ce projet offre la possibilité d'interroger un modèle de language large basé sur des documents spécifiques à une entreprise, permettant ainsi d'obtenir rapidement des réponses détaillées concernant leur contenu.

## Installation

Après avoir téléchargé le dossier AskLLM, ouvrez votre terminal et naviguez jusqu'au répertoire du dossier en utilisant la commande :

⁠ bash
cd path/to/AskLLM
 ⁠

Ensuite, procédez à l'installation des dépendances nécessaires avec la commande suivante :

⁠ bash
pip install -r requirements.txt
 ⁠

## Utilisation

### Extraction des informations depuis les PDF

Créez un fichier .env avec les informations suivantes:

    ROOT_DIR = .
    PDF_INPUT_FOLDER_PATH = "./[chemin_vers_dossier_contenant_pdf]"
    OUTPUT_FOLDER_PATH = "./[chemin_vers_dossier_de_sortie]"

    ADOBE_CLIENT_ID = "[clé_client_adobe]"
    ADOBE_CLIENT_SECRET = "[clé_secret_client_adobe]"

    OPENAI_API_KEY = "[clé_api_openai]"

### Extraction des informations depuis les PDF

⁠ bash
python src/pipeline.py
 ⁠

Le fichier ⁠ pipeline.py ⁠ traite tous les PDF présents dans le dossier d'entrée (dont le chemin doit être défini comme une variable d'environnement) et utilise l'API Adobe pour en extraire les textes et les tableaux. Ces informations sont ensuite sauvegardées dans un fichier CSV contenant tous les textes extraits des PDF.

### Concaténation des informations récupérées

Pour les fichiers PDF dont le contenu extrait présente un nombre excessif de lignes (c'est-à-dire que les paragraphes sont trop segmentés), une opération de concaténation est recommandée. Cette opération regroupe les textes appartenant aux mêmes pages de chaque PDF pour les réunir en une seule ligne dans le fichier CSV.

⁠ bash
python src/pdf_concatenation.py
 ⁠

### Vectorisation des textes

Exécutez le script embedding_dataset_openai.py pour vectoriser chaque morceau de texte en utilisant l'API d'OpenAI. 

⁠ bash
python src/embedding_dataset_openai.py
 ⁠

### Requête au LLM

Exécutez le script prompting_chatgpt.py pour poser une question a chatgpt basé sur les documents du corpus de pdf. 

⁠ bash
python src/prompting_chatgpt.py
 ⁠
Vous pouvez aussi utiliser mistral pour cette phase, en utilisant le script prompting_mistral.py . Ce script utilise toujours l'API D'OpenAI pour vectoriser la question de l'utilisateur. 

bash
python src/prompting_mistral.py


Assurez-vous de remplacer ⁠ path/to/AskLLM par le chemin réel vers le dossier ⁠ ExpansIA ⁠ sur votre machine, et de suivre les instructions de configuration spécifiques pour l'utilisation des APIs ou outils mentionnés.


## Contribution
Lucas McIntyre
