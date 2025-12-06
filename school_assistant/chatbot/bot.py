#!/usr/bin/env python3
"""
Chatbot RAG amélioré avec support multi-LLM
- OpenAI (si clé API disponible)
- Ollama (local, gratuit)
- Fallback sur recherche documentaire
"""
import os
import sys
from dotenv import load_dotenv
from typing import Optional, List
from langchain_core.documents import Document

# Imports protégés
try:
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import SentenceTransformerEmbeddings
except ImportError as e:
    print(f"ERREUR D'IMPORT CRITIQUE: {e}")
    print("Installez les dépendances: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()


def _format_excerpts(docs: List[Document]) -> str:
    """Formate les extraits de documents de manière lisible."""
    formatted = ""
    for i, doc in enumerate(docs, start=1):
        content = doc.page_content.strip()
        source = doc.metadata.get('source', 'Unknown')
        doc_type = doc.metadata.get('doc_type', 'Unknown')
        
        # Aperçu de 300 caractères
        snippet = content[:300]
        if len(content) > 300:
            snippet += "…"
        
        formatted += f"\n📄 **{i}. [{doc_type}] {source}**\n{snippet}\n"
    
    return formatted


def _try_groq(context: str, question: str) -> Optional[str]:
    """Tente d'utiliser Groq (priorité 1 - gratuit et rapide)."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return None
    
    try:
        from langchain_groq import ChatGroq
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0
        )
        
        prompt = f"""Tu es un assistant scolaire spécialisé dans les règlements de l'Académie Provinciale des Métiers (APM).

Utilise UNIQUEMENT les informations suivantes pour répondre à la question.
Si la réponse n'est pas dans le contexte, dis-le clairement.

CONTEXTE DES RÈGLEMENTS :
{context}

QUESTION : {question}

RÉPONSE (en français, claire et concise) :"""

        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return None


def _try_openai(context: str, question: str) -> Optional[str]:
    """Tente d'utiliser OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return None
    
    try:
        from langchain_openai import ChatOpenAI  # Compatible DeepSeek
        
        llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            openai_api_key=api_key
        )
        
        prompt = f"""Tu es un assistant scolaire spécialisé dans les règlements de l'Académie Provinciale des Métiers (APM).

Utilise UNIQUEMENT les informations suivantes pour répondre à la question.
Si la réponse n'est pas dans le contexte, dis-le clairement.

CONTEXTE DES RÈGLEMENTS :
{context}

QUESTION : {question}

RÉPONSE (en français, claire et concise) :"""

        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg or "429" in error_msg:
            return None  # Quota épuisé, essayer Ollama
        raise


def _try_ollama(context: str, question: str) -> Optional[str]:
    """Tente d'utiliser Ollama."""
    try:
        from langchain_community.llms import Ollama
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "mistral")
        
        llm = Ollama(
            base_url=base_url,
            model=model,
            temperature=0
        )
        
        prompt = f"""Tu es un assistant scolaire spécialisé dans les règlements de l'APM.

Utilise UNIQUEMENT les informations suivantes pour répondre.

CONTEXTE :
{context}

QUESTION : {question}

RÉPONSE (française, concise) :"""

        response = llm.invoke(prompt)
        return response
        
    except Exception as e:
        # Ollama non installé ou non démarré
        return None


def ask_bot(question: str, verbose: bool = True):
    """
    Recherche et répond à une question sur les règlements.
    
    Stratégie de fallback :
    1. OpenAI (si clé valide)
    2. Ollama (si installé et démarré)
    3. Recherche documentaire (toujours disponible)
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, "data", "faiss_index")

    # 1. Charger la base FAISS
    if verbose:
        print(f"\n🔍 Recherche pour : '{question}'")
    
    try:
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        db = FAISS.load_local(db_dir, embedding_function, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la base : {e}")
        print(f"   Exécutez d'abord : python school_assistant/chatbot/setup_rag.py")
        return

    # 2. Récupérer les documents pertinents
    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    
    if not docs:
        print("\n⚠️  Aucun document pertinent trouvé.")
        return
    
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 3. Stratégie de génération de réponse
    if verbose:
        print("💭 Génération de la réponse...")
    
    # Tentative 1 : Groq (priorité - gratuit et rapide)
    try:
        response = _try_groq(context, question)
        if response:
            if verbose:
                print("   ✅ Utilisation : Groq (Llama 3.3)")
            print(f"\n{'='*70}")
            print("📝 RÉPONSE")
            print('='*70)
            print(response)
            print('='*70)
            return
    except Exception as e:
        if verbose:
            print(f"   ⚠️  Groq indisponible : {e}")
    
    # Tentative 2 : OpenAI/DeepSeek
    try:
        response = _try_openai(context, question)
        if response:
            if verbose:
                print("   ✅ Utilisation : OpenAI/DeepSeek")
            print(f"\n{'='*70}")
            print("📝 RÉPONSE")
            print('='*70)
            print(response)
            print('='*70)
            return
    except Exception as e:
        if verbose:
            print(f"   ⚠️  OpenAI indisponible : {e}")
    
    # Tentative 3 : Ollama
    try:
        response = _try_ollama(context, question)
        if response:
            if verbose:
                print("   ✅ Utilisation : Ollama (local)")
            print(f"\n{'='*70}")
            print("📝 RÉPONSE")
            print('='*70)
            print(response)
            print('='*70)
            return
    except Exception as e:
        if verbose:
            print(f"   ℹ️  Ollama non disponible")
    
    # Fallback : Recherche documentaire
    if verbose:
        print("   ℹ️  Mode : Recherche Documentaire")
        print(f"\n{'='*70}")
        print("📚 EXTRAITS PERTINENTS TROUVÉS")
        print('='*70)
    
    print(_format_excerpts(docs))
    print('='*70)
    print("\n💡 Pour une réponse synthétisée, installez Ollama :")
    print("   curl -fsSL https://ollama.com/install.sh | sh")
    print("   ollama pull mistral")


def interactive_mode():
    """Mode interactif en ligne de commande."""
    print("\n" + "="*70)
    print("🎓 ASSISTANT RÈGLEMENTS APM - Mode Interactif")
    print("="*70)
    print("Tapez 'exit' ou 'quit' pour quitter\n")
    
    while True:
        try:
            question = input("❓ Votre question : ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Au revoir !")
                break
            
            ask_bot(question)
            print()  # Ligne vide entre les questions
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Mode ligne de commande
        question = " ".join(sys.argv[1:])
        ask_bot(question)
    else:
        # Mode interactif
        interactive_mode()
