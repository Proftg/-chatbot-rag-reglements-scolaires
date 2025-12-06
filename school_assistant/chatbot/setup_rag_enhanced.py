"""
Setup RAG amélioré avec embeddings multilingues et chunking intelligent.
"""
import os
import sys
from pathlib import Path

# Ajouter le chemin pour les imports
sys.path.append(str(Path(__file__).parents[1]))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from scraper.enhanced_ingest import ingest_all_pdfs
from chatbot.chunking_strategy import smart_chunk_documents
from utils.logger import setup_logger

logger = setup_logger("setup_rag")


def build_enhanced_index():
    """
    Construit un index RAG amélioré avec:
    - Embeddings multilingues de qualité
    - Chunking intelligent selon le type de document
    - Métadonnées enrichies
    - Persistence avec ChromaDB
    """
    base_dir = Path(__file__).resolve().parents[1]
    pdf_dir = base_dir.parent / "Réglements"
    chroma_dir = base_dir / "data" / "chroma_db_enhanced"
    
    logger.info("=" * 60)
    logger.info("CONSTRUCTION DE L'INDEX RAG AMÉLIORÉ")
    logger.info("=" * 60)
    
    # 1. Ingestion des PDFs avec métadonnées
    logger.info("\n📥 Étape 1: Ingestion des PDFs...")
    if not pdf_dir.exists():
        logger.error(f"❌ Dossier PDFs introuvable: {pdf_dir}")
        return
    
    documents = ingest_all_pdfs(pdf_dir)
    logger.info(f"✅ {len(documents)} pages extraites")
    
    if not documents:
        logger.error("❌ Aucun document extrait. Arrêt.")
        return
    
    # 2. Chunking intelligent
    logger.info("\n✂️  Étape 2: Découpage intelligent des documents...")
    chunks = smart_chunk_documents(documents)
    logger.info(f"✅ {len(chunks)} chunks créés")
    
    # 3. Configuration des embeddings multilingues
    logger.info("\n🧠 Étape 3: Chargement du modèle d'embeddings multilingue...")
    logger.info("   Modèle: paraphrase-multilingual-mpnet-base-v2")
    logger.info("   (Optimisé pour le français, 768 dimensions)")
    
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    logger.info("✅ Modèle chargé")
    
    # 4. Création de la base vectorielle ChromaDB
    logger.info(f"\n💾 Étape 4: Création de la base ChromaDB...")
    logger.info(f"   Destination: {chroma_dir}")
    
    # Supprimer l'ancienne DB si elle existe
    if chroma_dir.exists():
        import shutil
        shutil.rmtree(chroma_dir)
        logger.info("   🗑️  Ancienne DB supprimée")
    
    # Créer la nouvelle DB avec les chunks
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=str(chroma_dir),
        collection_name="reglements_ecole",
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    logger.info(f"✅ Base créée avec {len(chunks)} chunks indexés")
    
    # 5. Validation
    logger.info("\n🔍 Étape 5: Validation de l'index...")
    test_query = "absence professeur"
    results = db.similarity_search(test_query, k=3)
    
    logger.info(f"   Test de recherche: '{test_query}'")
    logger.info(f"   Résultats trouvés: {len(results)}")
    
    if results:
        logger.info(f"   Premier résultat: {results[0].metadata.get('source', 'N/A')}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ INDEX RAG AMÉLIORÉ CRÉÉ AVEC SUCCÈS!")
    logger.info("=" * 60)
    logger.info(f"\nStatistiques finales:")
    logger.info(f"  - PDFs traités: {len(list(pdf_dir.glob('*.pdf')))}")
    logger.info(f"  - Pages extraites: {len(documents)}")
    logger.info(f"  - Chunks indexés: {len(chunks)}")
    logger.info(f"  - Taille moyenne chunk: {sum(len(c.page_content) for c in chunks) // len(chunks)} caractères")
    logger.info(f"\n📍 Base de données: {chroma_dir}")


if __name__ == "__main__":
    build_enhanced_index()
