"""
Pipeline d'ingestion amélioré avec métadonnées et prétraitement.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict
import hashlib
from datetime import datetime

# Ajouter le chemin parent pour importer les utils
sys.path.append(str(Path(__file__).parents[1]))

from pypdf import PdfReader
from langchain_core.documents import Document
from utils.text_processing import preprocess_text, extract_section_title
from utils.logger import setup_logger

logger = setup_logger("enhanced_ingest")


def classify_document(filename: str) -> str:
    """
    Classifie le type de document basé sur son nom.
    
    Args:
        filename: Nom du fichier PDF
        
    Returns:
        Type de document (reglement, projet, protocole, etc.)
    """
    filename_lower = filename.lower()
    
    if "roi" in filename_lower or "règlement d'ordre" in filename_lower:
        return "reglement_ordre_interieur"
    elif "rge" in filename_lower or "règlement général" in filename_lower:
        return "reglement_general_etudes"
    elif "projet" in filename_lower:
        return "projet_educatif"
    elif "protocole" in filename_lower:
        return "protocole"
    elif "dress code" in filename_lower:
        return "dress_code"
    elif "règlement" in filename_lower:
        return "reglement_specifique"
    else:
        return "autre"


def extract_pdf_with_metadata(pdf_path: Path) -> List[Document]:
    """
    Extrait le texte d'un PDF avec métadonnées enrichies.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        Liste de documents avec métadonnées
    """
    documents = []
    doc_type = classify_document(pdf_path.name)
    
    logger.info(f"Extraction de {pdf_path.name} (type: {doc_type})")
    
    try:
        reader = PdfReader(str(pdf_path))
        
        for page_num, page in enumerate(reader.pages):
            raw_text = page.extract_text()
            
            # Validation
            if not raw_text or len(raw_text.strip()) < 50:
                logger.warning(f"Page {page_num} de {pdf_path.name} trop courte ou vide")
                continue
            
            # Prétraitement
            clean_text = preprocess_text(raw_text)
            
            if len(clean_text) < 30:
                logger.warning(f"Page {page_num} de {pdf_path.name} vide après nettoyage")
                continue
            
            # Hash pour détecter les duplications
            content_hash = hashlib.sha256(clean_text.encode()).hexdigest()[:16]
            
            # Extraire un titre si possible
            section_title = extract_section_title(clean_text)
            
            # Créer le document avec métadonnées
            documents.append(Document(
                page_content=clean_text,
                metadata={
                    "source": pdf_path.name,
                    "page": page_num + 1,  # Numérotation humaine (1-indexed)
                    "doc_type": doc_type,
                    "content_hash": content_hash,
                    "section_title": section_title,
                    "char_count": len(clean_text),
                    "processed_at": datetime.now().isoformat()
                }
            ))
            
        logger.info(f"✅ {pdf_path.name}: {len(documents)} pages extraites")
        
    except Exception as e:
        logger.error(f"❌ Erreur sur {pdf_path.name}: {e}", exc_info=True)
    
    return documents


def ingest_all_pdfs(pdf_folder: Path) -> List[Document]:
    """
    Ingère tous les PDFs d'un dossier.
    
    Args:
        pdf_folder: Dossier contenant les PDFs
        
    Returns:
        Liste de tous les documents extraits
    """
    if not pdf_folder.is_dir():
        logger.error(f"Dossier introuvable: {pdf_folder}")
        raise FileNotFoundError(f"Le dossier PDF n'existe pas : {pdf_folder}")
    
    logger.info(f"Début de l'ingestion depuis: {pdf_folder}")
    logger.info(f"Contenu du dossier: {list(pdf_folder.glob('*.pdf'))}")
    
    all_documents = []
    
    for pdf_path in pdf_folder.glob("*.pdf"):
        docs = extract_pdf_with_metadata(pdf_path)
        all_documents.extend(docs)
    
    logger.info(f"✅ Ingestion terminée: {len(all_documents)} documents extraits de {len(list(pdf_folder.glob('*.pdf')))} PDFs")
    
    return all_documents


if __name__ == "__main__":
    # Chemins
    pdf_dir = Path(__file__).resolve().parents[2] / "Réglements"
    
    # Test de l'ingestion
    documents = ingest_all_pdfs(pdf_dir)
    
    # Afficher quelques stats
    print(f"\n📊 Statistiques:")
    print(f"  Total documents: {len(documents)}")
    
    doc_types = {}
    for doc in documents:
        dt = doc.metadata['doc_type']
        doc_types[dt] = doc_types.get(dt, 0) + 1
    
    print(f"\n  Par type:")
    for dt, count in doc_types.items():
        print(f"    - {dt}: {count}")
