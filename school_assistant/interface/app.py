import streamlit as st
import os
import sys

# Ajouter le dossier parent au path pour importer les modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scraper.fetch_notes import fetch_content
from daily_check import send_email, RECEIVER_EMAIL
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Assistant École",
    page_icon="🎓",
    layout="wide"
)

# Fonction pour charger le bot (similaire à bot.py)
@st.cache_resource
def load_rag_engine():
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import SentenceTransformerEmbeddings
        from dotenv import load_dotenv
        
        load_dotenv()
        
        base_dir = os.path.dirname(parent_dir) # AMP/
        db_dir = os.path.join(base_dir, "school_assistant", "data", "faiss_index")
        
        if not os.path.exists(db_dir):
            return None, None
            
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        db = FAISS.load_local(db_dir, embedding_function, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        
        # Retourner le retriever et la clé API (Groq ou OpenAI)
        return retriever, os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    except Exception as e:
        st.error(f"Erreur chargement IA: {e}")
        return None, None

st.title("🎓 Assistant Scolaire Intégré")

# Onglets pour les différentes fonctionnalités
tab1, tab2, tab3 = st.tabs(["🤖 Chatbot Règlements", "📋 Notes de Service", "⚙️ Système & Logs"])

with tab1:
    st.header("Posez vos questions sur le règlement")
    retriever, api_key = load_rag_engine()
    
    if retriever:
        # Historique de chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ex: Comment justifier une absence ?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Logique RAG avec Groq en priorité
                docs = retriever.invoke(prompt)
                context_text = "\n\n".join([d.page_content for d in docs])
                
                response_text = ""
                
                # Tentative 1 : Groq (priorité - gratuit et rapide)
                groq_key = os.getenv("GROQ_API_KEY")
                if groq_key:
                    try:
                        from langchain_groq import ChatGroq
                        llm = ChatGroq(
                            model="llama-3.3-70b-versatile",
                            groq_api_key=groq_key,
                            temperature=0
                        )
                        full_prompt = f"Tu es un assistant scolaire. Utilise ce contexte pour répondre: {context_text}\n\nQuestion: {prompt}"
                        ai_msg = llm.invoke(full_prompt)
                        response_text = ai_msg.content
                    except Exception as e:
                        st.info(f"Groq indisponible : {e}")
                        groq_key = None  # Essayer la méthode suivante
                
                # Tentative 2 : DeepSeek/OpenAI (si Groq a échoué)
                if not response_text and api_key:
                    try:
                        from langchain_openai import ChatOpenAI
                        llm = ChatOpenAI(
                            model="deepseek-chat",
                            openai_api_key=api_key,
                            openai_api_base="https://api.deepseek.com/v1",
                            temperature=0
                        )
                        full_prompt = f"Tu es un assistant scolaire. Utilise ce contexte pour répondre: {context_text}\n\nQuestion: {prompt}"
                        ai_msg = llm.invoke(full_prompt)
                        response_text = ai_msg.content
                    except Exception as e:
                        st.info(f"DeepSeek/OpenAI indisponible : {e}")
                
                # Fallback : Recherche documentaire
                if not response_text:
                    response_text = f"ℹ️ **Mode Recherche Documentaire**\n\nVoici les extraits pertinents trouvés :\n\n{context_text}"
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
    else:
        st.warning("⚠️ L'index de recherche n'est pas prêt. Veuillez vérifier que 'setup_rag.py' a bien tourné.")

with tab2:
    st.header("Surveillance des Notes de Service")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📄 Dernier contenu extrait")
        # Lire le fichier local s'il existe
        notes_file = os.path.join(parent_dir, "data", "notes_latest.txt")
        if os.path.exists(notes_file):
            with open(notes_file, "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("Contenu brut", content, height=400)
        else:
            st.info("Aucune note téléchargée pour le moment.")
    
    with col2:
        st.markdown("### ⚡ Actions")
        if st.button("🔄 Forcer la vérification maintenant"):
            with st.spinner("Vérification en cours sur le site..."):
                try:
                    new_content = fetch_content()
                    if new_content:
                        st.success("✅ Vérification terminée ! La page a été téléchargée.")
                        st.rerun()
                    else:
                        st.error("❌ Échec de la connexion au site.")
                except Exception as e:
                    st.error(f"Erreur: {e}")

    st.markdown("---")
    st.markdown("### 📜 Règlements extraits")
    reg_file = os.path.join(parent_dir, "data", "reglement_raw.txt")
    if os.path.exists(reg_file):
        with open(reg_file, "r", encoding="utf-8") as f:
            reg_content = f.read()
        st.text_area("Contenu du Règlement", reg_content, height=300)
    else:
        st.info("Règlement non trouvé.")

with tab3:
    st.header("État du Système")
    st.markdown(f"**Email de notification :** `{RECEIVER_EMAIL}`")
    
    st.markdown("### 📂 Fichiers de données")
    data_dir = os.path.join(parent_dir, "data")
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        for f in files:
            file_path = os.path.join(data_dir, f)
            size = os.path.getsize(file_path) / 1024
            st.text(f"- {f} ({size:.1f} KB)")
    else:
        st.warning("Dossier 'data' introuvable.")

    st.markdown("### 🛠️ Outils de maintenance")
    if st.button("🗑️ Réinitialiser la base de connaissances (Clean DB)"):
        # Logique de nettoyage simple
        st.warning("Pour nettoyer, lancez 'python clean_db.py' dans le terminal.")
