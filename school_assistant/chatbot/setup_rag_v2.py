"""
Setup RAG amélioré avec embeddings multilingues et retrieval hybride
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.append(str(Path(__file__).parent.parent))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever

from scraper.enhanced_ingest import ingest_pdfs_enhanced
from chatbot.chunking_strategy import chunk_documents_smart, get_chunk_statistics
from utils.logger import setup_logger
import config

logger = setup_logger(__name__)


class MultilingualEmbeddings:
    """Wrapper pour utiliser HuggingFace embeddings avec LangChain."""
    
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        logger.info(f"Chargement du modèle d'embeddings: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info("Modèle chargé avec succès")
    
    def embed_documents(self, texts):
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text):
        return self.embeddings.embed_query(text)


def build_enhanced_index():
    """
    Construit un index RAG amélioré avec:
    - Ingestion avec métadonnées enrichies
    - Chunking intelligent adapté aux types de documents
    - Embeddings multilingues optimisés pour le français
    - Base de données vectorielle ChromaDB
    """
    logger.info("=" * 60)
    logger.info("DÉBUT DE LA CONSTRUCTION DE L'INDEX RAG AMÉLIORÉ")
    logger.info("=" * 60)
    
    # Étape 1: Ingestion des PDF
    logger.info("\n[1/4] Ingestion des PDF...")
    documents = ingest_pdfs_enhanced(
        pdf_folder=config.REGLEMENTS_DIR,
        output_folder=config.DATA_DIR,
        save_txt=True
    )
    
    if not documents:
        logger.error("Aucun document n'a été ingéré. Vérifiez le dossier PDF.")
        return False
    
    logger.info(f"✅ {len(documents)} documents ingérés")
    
    # Étape 2: Chunking intelligent
    logger.info("\n[2/4] Découpage intelligent des documents...")
    chunks = chunk_documents_smart(documents, preserve_metadata=True)
    
    # Statistiques
    stats = get_chunk_statistics(chunks)
    logger.info(f"Statistiques des chunks:")
    logger.info(f"  - Nombre total: {stats['total_chunks']}")
    logger.info(f"  - Taille moyenne: {stats['avg_size_chars']:.0f} caractères")
    logger.info(f"  - Tokens estimés (total): {stats['total_tokens_est']}")
    logger.info(f"  - Tokens moyens par chunk: {stats['avg_tokens']:.0f}")
    
    # Étape 3: Création des embeddings
    logger.info("\n[3/4] Création des embeddings multilingues...")
    embedding_function = MultilingualEmbeddings()
    
    # Étape 4: Indexation dans ChromaDB
    logger.info("\n[4/4] Indexation dans ChromaDB...")
    
    # Supprimer l'ancienne base si elle existe
    if config.DB_DIR.exists():
        import shutil
        shutil.rmtree(config.DB_DIR)
        logger.info("Ancienne base de données supprimée")
    
    # Créer la nouvelle base
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=str(config.DB_DIR),
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    logger.info(f"✅ Base de données créée dans {config.DB_DIR}")
    
    # Sauvegarder des métadonnées sur l'index
    metadata_file = config.DB_DIR / "index_metadata.txt"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write(f"Date de création: {Path(__file__).stat().st_mtime}\n")
        f.write(f"Nombre de chunks: {stats['total_chunks']}\n")
        f.write(f"Modèle d'embeddings: {config.EMBEDDING_MODEL}\n")
        f.write(f"Documents sources: {len(documents)}\n")
        f.write(f"Tokens estimés: {stats['total_tokens_est']}\n")
    
    logger.info("=" * 60)
    logger.info("✅ INDEXATION TERMINÉE AVEC SUCCÈS")
    logger.info("=" * 60)
    
    return True


def load_retriever(search_type="hybrid"):
    """
    Charge le retriever avec différentes stratégies.
    
    Args:
        search_type: "semantic", "lexical", ou "hybrid"
    
    Returns:
        Retriever configuré
    """
    logger.info(f"Chargement du retriever (mode: {search_type})")
    
    # Charger les embeddings
    embedding_function = MultilingualEmbeddings()
    
    # Charger la base vectorielle
    db = Chroma(
        persist_directory=str(config.DB_DIR),
        embedding_function=embedding_function
    )
    
    if search_type == "semantic":
        # Retrieval sémantique pur (FAISS/Chroma)
        retriever = db.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance
            search_kwargs={
                "k": config.RETRIEVER_K,
                "fetch_k": config.RETRIEVER_FETCH_K,
                "lambda_mult": 0.7  # Balance diversité/pertinence
            }
        )
        logger.info("Retriever sémantique (MMR) chargé")
        return retriever
    
    elif search_type == "lexical":
        # Retrieval lexical (BM25)
        # Récupérer tous les documents pour BM25
        all_docs = db.get()
        documents = [
            {"page_content": text, "metadata": meta}
            for text, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]
        
        retriever = BM25Retriever.from_texts(
            [doc["page_content"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents]
        )
        retriever.k = config.RETRIEVER_K
        logger.info("Retriever lexical (BM25) chargé")
        return retriever
    
    elif search_type == "hybrid":
        # Retrieval hybride (combine sémantique + lexical)
        semantic_retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": config.RETRIEVER_K,
                "fetch_k": config.RETRIEVER_FETCH_K,
            }
        )
        
        # BM25
        all_docs = db.get()
        documents = [
            {"page_content": text, "metadata": meta}
            for text, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]
        
        bm25_retriever = BM25Retriever.from_texts(
            [doc["page_content"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents]
        )
        bm25_retriever.k = config.RETRIEVER_K
        
        # Ensemble avec pondération
        ensemble_retriever = EnsembleRetriever(
            retrievers=[semantic_retriever, bm25_retriever],
            weights=[0.7, 0.3]  # 70% sémantique, 30% lexical
        )
        
        logger.info("Retriever hybride (70% sémantique + 30% lexical) chargé")
        return ensemble_retriever
    
    else:
        raise ValueError(f"Type de search inconnu: {search_type}")


if __name__ == "__main__":
    success = build_enhanced_index()
    if success:
        print("\n✅ Index construit avec succès!")
        print(f"Base de données: {config.DB_DIR}")
    else:
        print("\n❌ Échec de la construction de l'index")
