"""
Prétraitement et nettoyage de texte pour améliorer la qualité des embeddings.
"""
import re
from typing import List


def preprocess_text(text: str) -> str:
    """
    Nettoie le texte extrait des PDFs.
    
    Args:
        text: Texte brut à nettoyer
        
    Returns:
        Texte nettoyé et normalisé
    """
    # Suppression des métadonnées web (likes, comments, etc.)
    text = re.sub(r'\b(likes|comments|add comment|pdf)\b', '', text, flags=re.IGNORECASE)
    
    # Normalisation des espaces multiples
    text = re.sub(r' +', ' ', text)
    
    # Normalisation des sauts de ligne multiples (garder max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Suppression des numéros de page isolés
    text = re.sub(r'\n\d+\n', '\n', text)
    
    # Suppression des lignes très courtes (probablement du bruit)
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if len(line.strip()) > 3 or line.strip() == '']
    text = '\n'.join(cleaned_lines)
    
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Découpe le texte en phrases de manière intelligente.
    
    Args:
        text: Texte à découper
        
    Returns:
        Liste de phrases
    """
    # Pattern pour détecter les fins de phrases
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def extract_section_title(text: str) -> str:
    """
    Extrait le titre d'une section si présent.
    
    Args:
        text: Texte contenant potentiellement un titre
        
    Returns:
        Titre extrait ou chaîne vide
    """
    lines = text.split('\n')
    if lines:
        first_line = lines[0].strip()
        # Si la première ligne est courte et en majuscules ou commence par un numéro
        if len(first_line) < 100 and (first_line.isupper() or re.match(r'^\d+\.', first_line)):
            return first_line
    return ""
