"""
Bot RAG amélioré avec retrieval hybride et métadonnées.
"""
import os
import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Ajouter le chemin pour les imports
sys.path.append(str(Path(__file__).parents[1]))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("bot_enhanced")


def format_results_with_metadata(docs: List[Document]) -> str:
    """
    Formate les résultats avec métadonnées pour affichage à l'utilisateur.
    
    Args:
        docs: Documents trouvés
        
    Returns:
        Texte formaté
    """
    formatted = ""
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get('source', 'Source inconnue')
        page = doc.metadata.get('page', '?')
        doc_type = doc.metadata.get('doc_type', 'N/A')
        section = doc.metadata.get('section_title', '')
        
        formatted += f"\n📄 **Résultat {i}** - {source} (page {page})\n"
        if section:
            formatted += f"   Section: {section}\n"
        formatted += f"   Type: {doc_type}\n"
        
        # Extrait du contenu (limité à 300 caractères)
        content = doc.page_content.strip()
        if len(content) > 300:
            content = content[:300] + "..."
        formatted += f"   Extrait: {content}\n"
    
    return formatted


def ask_bot_enhanced(question: str, k: int = 5):
    """
    Recherche améliorée avec retrieval hybride et formatage enrichi.
    
    Args:
        question: Question de l'utilisateur
        k: Nombre de documents à récupérer
    """
    base_dir = Path(__file__).resolve().parents[1]
    chroma_dir = base_dir / "data" / "chroma_db_enhanced"
    
    # Vérifier que la DB existe
    if not chroma_dir.exists():
        logger.error(f"❌ Base de données introuvable: {chroma_dir}")
        print("\n⚠️ La base de données n'existe pas encore.")
        print("   Veuillez d'abord exécuter: python school_assistant/chatbot/setup_rag_enhanced.py")
        return
    
    # Charger les embeddings
    logger.info("Chargement du modèle d'embeddings...")
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Charger la DB
    logger.info("Chargement de la base vectorielle...")
    db = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embedding_function,
        collection_name="reglements_ecole"
    )
    
    # Recherche avec MMR (Maximum Marginal Relevance) pour la diversité
    logger.info(f"🔍 Recherche pour: '{question}'")
    print(f"\n🤖 Recherche en cours pour: '{question}'\n")
    
    docs = db.similarity_search(
        question,
        k=k,
    )
    
    if not docs:
        print("❌ Aucun document pertinent trouvé.")
        logger.warning("Aucun résultat trouvé")
        return
    
    logger.info(f"✅ {len(docs)} documents trouvés")
    
    # Préparer le contexte
    context = "\n\n---\n\n".join([
        f"[Source: {doc.metadata.get('source', 'N/A')}, Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
        for doc in docs
    ])
    
    # Utiliser l'IA si disponible
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        logger.info("Génération de la réponse avec GPT...")
        try:
            llm = ChatOpenAI(
                temperature=0,
                model_name="gpt-3.5-turbo",
                openai_api_key=api_key
            )
            
            prompt = f"""Tu es un assistant scolaire spécialisé dans les règlements d'établissement belges.

Réponds à la question de l'utilisateur en te basant UNIQUEMENT sur le contexte fourni ci-dessous.

INSTRUCTIONS:
- Sois précis et concis
- Cite les sources (nom du document et numéro de page)
- Si la réponse n'est pas dans le contexte, dis-le clairement
- Utilise un langage professionnel mais accessible

CONTEXTE:
{context}

QUESTION: {question}

RÉPONSE:"""

            response = llm.invoke(prompt)
            
            print("=" * 70)
            print("💡 RÉPONSE GÉNÉRÉE PAR L'IA")
            print("=" * 70)
            print(response.content)
            print("\n" + "=" * 70)
            print("📚 SOURCES CONSULTÉES")
            print("=" * 70)
            print(format_results_with_metadata(docs))
            
            logger.info("✅ Réponse générée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur IA: {e}")
            print(f"\n⚠️ Erreur avec l'IA: {e}")
            print("\n📋 Résultats bruts de la recherche:")
            print(format_results_with_metadata(docs))
    else:
        logger.info("Mode recherche documentaire (pas de clé OpenAI)")
        print("ℹ️ Mode Recherche Documentaire (clé OpenAI absente)\n")
        print("=" * 70)
        print("📚 DOCUMENTS PERTINENTS TROUVÉS")
        print("=" * 70)
        print(format_results_with_metadata(docs))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        ask_bot_enhanced(query)
    else:
        print("Usage: python bot_enhanced.py 'Votre question ici'")
        print("\nExemple:")
        print("  python bot_enhanced.py 'Quelle est la procédure en cas d'absence de professeur?'")
