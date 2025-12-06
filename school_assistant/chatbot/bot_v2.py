"""
Chatbot amélioré avec retrieval hybride et meilleure gestion des réponses
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from chatbot.setup_rag_v2 import load_retriever
from utils.logger import setup_logger
import config

logger = setup_logger(__name__)

# Imports optionnels pour l'IA
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("langchain_openai non disponible, mode recherche documentaire uniquement")


def format_documents(docs, max_docs=3) -> str:
    """
    Formate les documents récupérés de manière lisible.
    
    Args:
        docs: Liste de documents
        max_docs: Nombre maximum de documents à afficher
    
    Returns:
        Texte formaté
    """
    if not docs:
        return "Aucun document pertinent trouvé."
    
    formatted = []
    for i, doc in enumerate(docs[:max_docs], 1):
        content = doc.page_content.strip()
        metadata = doc.metadata
        
        # Créer un en-tête informatif
        source = metadata.get('source', 'Source inconnue')
        page = metadata.get('page', '?')
        doc_type = metadata.get('doc_type', 'document')
        section = metadata.get('section_title', '')[:100]
        
        header = f"[{i}] {source} (page {page}, type: {doc_type})"
        if section:
            header += f"\n    Section: {section}"
        
        # Extraire un snippet pertinent (premiers 400 caractères)
        snippet = content[:400]
        if len(content) > 400:
            snippet += "..."
        
        formatted.append(f"{header}\n{snippet}\n")
    
    return "\n".join(formatted)


def ask_bot_v2(question: str, search_type="hybrid", verbose=False):
    """
    Répond à une question en utilisant le système RAG amélioré.
    
    Args:
        question: Question posée
        search_type: Type de recherche ("semantic", "lexical", "hybrid")
        verbose: Si True, affiche des détails supplémentaires
    
    Returns:
        Réponse formatée
    """
    logger.info(f"Question reçue: {question}")
    logger.info(f"Mode de recherche: {search_type}")
    
    try:
        # 1. Charger le retriever
        retriever = load_retriever(search_type=search_type)
        
        # 2. Récupérer les documents pertinents
        print(f"\n🔍 Recherche en cours (mode: {search_type})...")
        docs = retriever.invoke(question)
        
        if verbose:
            print(f"\n📚 {len(docs)} documents trouvés")
            for i, doc in enumerate(docs, 1):
                print(f"  [{i}] {doc.metadata.get('source', '?')} - "
                      f"page {doc.metadata.get('page', '?')} - "
                      f"{len(doc.page_content)} caractères")
        
        # 3. Préparer le contexte
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        
        # 4. Générer la réponse
        if config.OPENAI_API_KEY and OPENAI_AVAILABLE:
            print("\n🤖 Génération de la réponse avec GPT...\n")
            
            try:
                llm = ChatOpenAI(
                    temperature=config.LLM_TEMPERATURE,
                    model_name=config.OPENAI_MODEL,
                    openai_api_key=config.OPENAI_API_KEY
                )
                
                prompt = f"""Tu es un assistant scolaire expert qui aide les enseignants et le personnel à comprendre les règlements et procédures de l'école.

CONTEXTE (extraits des règlements officiels) :
{context}

QUESTION : {question}

INSTRUCTIONS :
1. Réponds de manière précise et professionnelle en te basant UNIQUEMENT sur le contexte fourni
2. Si la réponse n'est pas dans le contexte, dis-le clairement
3. Structure ta réponse de manière claire avec des points si nécessaire
4. Cite les sources quand c'est pertinent (nom du document, article)
5. Si plusieurs procédures sont possibles, liste-les toutes

RÉPONSE :"""
                
                response = llm.invoke(prompt)
                
                print("=" * 80)
                print("RÉPONSE")
                print("=" * 80)
                print(response.content)
                print("=" * 80)
                
                # Afficher les sources
                if verbose:
                    print("\n📖 SOURCES CONSULTÉES:")
                    print(format_documents(docs, max_docs=5))
                
                return response.content
                
            except Exception as e:
                logger.error(f"Erreur lors de l'appel à OpenAI: {e}")
                print(f"\n⚠️  L'IA n'est pas disponible (erreur: {e})")
                print("Affichage des extraits pertinents à la place...\n")
        
        # Mode sans IA: afficher les documents pertinents
        print("=" * 80)
        print("DOCUMENTS PERTINENTS TROUVÉS")
        print("=" * 80)
        print(format_documents(docs, max_docs=5))
        print("=" * 80)
        
        return format_documents(docs, max_docs=5)
        
    except Exception as e:
        logger.error(f"Erreur dans ask_bot_v2: {e}", exc_info=True)
        print(f"\n❌ Erreur: {e}")
        return None


def interactive_mode():
    """Mode interactif pour tester le chatbot."""
    print("\n" + "=" * 80)
    print("CHATBOT SCOLAIRE - MODE INTERACTIF")
    print("=" * 80)
    print("\nCommandes disponibles:")
    print("  - Tapez votre question")
    print("  - 'quit' ou 'exit' pour quitter")
    print("  - 'mode [semantic|lexical|hybrid]' pour changer le mode de recherche")
    print("  - 'verbose [on|off]' pour activer/désactiver les détails")
    print("=" * 80)
    
    search_mode = "hybrid"
    verbose = False
    
    while True:
        try:
            question = input("\n💬 Votre question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir!")
                break
            
            if question.lower().startswith('mode '):
                new_mode = question.split()[1].lower()
                if new_mode in ['semantic', 'lexical', 'hybrid']:
                    search_mode = new_mode
                    print(f"✅ Mode changé: {search_mode}")
                else:
                    print("❌ Mode invalide. Options: semantic, lexical, hybrid")
                continue
            
            if question.lower().startswith('verbose '):
                setting = question.split()[1].lower()
                if setting == 'on':
                    verbose = True
                    print("✅ Mode verbose activé")
                elif setting == 'off':
                    verbose = False
                    print("✅ Mode verbose désactivé")
                continue
            
            # Poser la question
            ask_bot_v2(question, search_type=search_mode, verbose=verbose)
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            logger.error(f"Erreur: {e}", exc_info=True)
            print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Chatbot scolaire amélioré")
    parser.add_argument("question", nargs="*", help="Question à poser")
    parser.add_argument("--mode", choices=["semantic", "lexical", "hybrid"], 
                        default="hybrid", help="Mode de recherche")
    parser.add_argument("--verbose", action="store_true", help="Afficher les détails")
    parser.add_argument("--interactive", "-i", action="store_true", 
                        help="Mode interactif")
    
    args = parser.parse_args()
    
    if args.interactive or not args.question:
        interactive_mode()
    else:
        question = " ".join(args.question)
        ask_bot_v2(question, search_type=args.mode, verbose=args.verbose)
