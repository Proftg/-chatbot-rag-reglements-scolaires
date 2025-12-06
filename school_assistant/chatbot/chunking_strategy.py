"""
Stratégies de chunking intelligentes adaptées au type de document.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document


def create_smart_chunker(doc_type: str) -> RecursiveCharacterTextSplitter:
    """
    Retourne un chunker adapté au type de document.
    
    Args:
        doc_type: Type de document (reglement, projet, etc.)
        
    Returns:
        Chunker configuré
    """
    # Séparateurs pour les documents administratifs français
    french_admin_separators = [
        "\n\n## ",      # Titres niveau 2
        "\n\n# ",       # Titres niveau 1  
        "\n\nArticle ",  # Articles de règlement
        "\n\n",         # Paragraphes
        "\n",           # Lignes
        ". ",           # Phrases
        " ",            # Mots
        ""
    ]
    
    if "reglement" in doc_type:
        # Règlements: chunks plus longs pour garder le contexte légal
        return RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            separators=french_admin_separators,
            length_function=len,
        )
    elif doc_type == "projet_educatif":
        # Projets: chunks moyens
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=french_admin_separators,
            length_function=len,
        )
    else:
        # Autres documents: configuration par défaut
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=french_admin_separators,
            length_function=len,
        )


def smart_chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Découpe intelligemment les documents selon leur type.
    
    Args:
        documents: Liste de documents avec métadonnées
        
    Returns:
        Liste de chunks avec métadonnées préservées
    """
    all_chunks = []
    
    # Grouper par type de document
    docs_by_type = {}
    for doc in documents:
        doc_type = doc.metadata.get('doc_type', 'autre')
        if doc_type not in docs_by_type:
            docs_by_type[doc_type] = []
        docs_by_type[doc_type].append(doc)
    
    # Chunker chaque groupe avec la stratégie appropriée
    for doc_type, docs in docs_by_type.items():
        chunker = create_smart_chunker(doc_type)
        chunks = chunker.split_documents(docs)
        
        # Ajouter l'ID du chunk aux métadonnées
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            chunk.metadata['total_chunks'] = len(chunks)
        
        all_chunks.extend(chunks)
        print(f"  {doc_type}: {len(docs)} docs → {len(chunks)} chunks")
    
    return all_chunks
