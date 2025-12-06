"""
Configuration centralisée pour School Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REGLEMENTS_DIR = PROJECT_ROOT / "Réglements"
LOGS_DIR = PROJECT_ROOT / "logs"
DB_DIR = DATA_DIR / "chroma_db_v2"

# Assurez-vous que les dossiers existent
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Modèle d'embeddings
# Options: 
# - "all-MiniLM-L6-v2" (anglais, rapide, 384 dimensions)
# - "paraphrase-multilingual-mpnet-base-v2" (multilingue, meilleur pour français, 768 dimensions)
# - "dangvantuan/sentence-camembert-large" (français spécialisé)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Configuration RAG
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_K = 5  # Nombre de documents à récupérer
RETRIEVER_FETCH_K = 20  # Pool initial pour MMR

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Validation
REQUIRED_ENV_VARS = ["SENDER_EMAIL", "GMAIL_APP_PASSWORD", "RECEIVER_EMAIL"]

def validate_config() -> list:
    """
    Valide que toutes les variables d'environnement requises sont présentes.
    
    Returns:
        Liste des variables manquantes (vide si tout est OK)
    """
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)
    return missing
