#!/usr/bin/env python3
"""
Script d'indexation RAG amélioré - Utilise tous les PDFs locaux
"""
import os
import glob
import re
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from datetime import datetime

def preprocess_text(text: str) -> str:
    """Nettoie le texte extrait."""
    # Suppression des métadonnées web
    text = re.sub(r'(likes|comments|add comment|share|skip to content)', '', text, flags=re.IGNORECASE)
    # Normalisation des espaces
    text = re.sub(r'\s+', ' ', text)
    # Normalisation des sauts de ligne
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def classify_document(filename: str) -> str:
    """Classifie le type de document selon son nom."""
    filename_lower = filename.lower()
    if 'roi' in filename_lower:
        return 'ROI'
    elif 'rge' in filename_lower or 'règlement général' in filename_lower:
        return 'RGE'
    elif 'projet' in filename_lower:
        return 'Projet'
    elif 'protocole' in filename_lower:
        return 'Protocole'
    elif 'règlement' in filename_lower or 'reglement' in filename_lower:
        return 'Règlement'
    elif 'dress code' in filename_lower:
        return 'Dress Code'
    else:
        return 'Autre'

def load_all_documents():
    """Charge tous les documents .txt du dossier data."""
    base_dir = Path(__file__).resolve().parents[2]
    data_dir = base_dir / "data"
    
    if not data_dir.exists():
        print(f"❌ Erreur: Le dossier {data_dir} n'existe pas.")
        return []
    
    print(f"📂 Chargement des documents depuis : {data_dir}")
    
    documents = []
    txt_files = list(data_dir.glob("*.txt"))
    
    # Filtrer les fichiers temporaires
    txt_files = [f for f in txt_files if not any(skip in f.name for skip in ['notes_', 'reglement_raw', 'previous', 'latest'])]
    
    print(f"   Trouvé {len(txt_files)} fichiers à traiter\n")
    
    for txt_file in txt_files:
        try:
            print(f"📄 Chargement : {txt_file.name}")
            
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validation
            if len(content) < 100:
                print(f"   ⚠️  Fichier trop court ({len(content)} caractères) - ignoré")
                continue
            
            # Nettoyage
            clean_content = preprocess_text(content)
            
            # Création du document avec métadonnées
            doc = Document(
                page_content=clean_content,
                metadata={
                    "source": txt_file.stem + ".pdf",  # Nom du PDF original
                    "doc_type": classify_document(txt_file.name),
                    "char_count": len(clean_content),
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            documents.append(doc)
            print(f"   ✅ {len(clean_content):,} caractères - Type: {doc.metadata['doc_type']}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    return documents

def build_index():
    """Construit l'index FAISS avec chunking optimisé."""
    print("="*70)
    print("   CONSTRUCTION DE L'INDEX RAG AMÉLIORÉ")
    print("="*70 + "\n")
    
    # 1. Chargement des documents
    documents = load_all_documents()
    
    if not documents:
        print("\n❌ Aucun document chargé. Exécutez d'abord ingest_local_pdfs.py")
        return
    
    total_chars = sum(len(doc.page_content) for doc in documents)
    print(f"\n📚 Total : {len(documents)} documents chargés ({total_chars:,} caractères)")
    
    # 2. Découpage en chunks
    print(f"\n📊 Découpage en chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,         # Augmenté de 500 à 1000
        chunk_overlap=200,       # Augmenté de 50 à 200
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"   ✅ {len(chunks)} chunks créés")
    
    # Statistiques
    chunk_sizes = [len(chunk.page_content) for chunk in chunks]
    print(f"   📏 Taille moyenne : {sum(chunk_sizes) // len(chunk_sizes)} caractères")
    print(f"   📏 Min: {min(chunk_sizes)}, Max: {max(chunk_sizes)}")
    
    # Afficher distribution par type de document
    doc_types = {}
    for chunk in chunks:
        dtype = chunk.metadata.get('doc_type', 'Autre')
        doc_types[dtype] = doc_types.get(dtype, 0) + 1
    
    print(f"\n   📋 Distribution par type :")
    for dtype, count in sorted(doc_types.items(), key=lambda x: -x[1]):
        print(f"      • {dtype}: {count} chunks")
    
    # 3. Calcul des embeddings
    print(f"\n🧠 Calcul des embeddings avec all-MiniLM-L6-v2...")
    print(f"   ⚠️  Note: Pour le français, considérez 'sentence-camembert-large'")
    
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 4. Construction de l'index FAISS
    print(f"\n💾 Construction de l'index FAISS...")
    base_dir = Path(__file__).resolve().parents[1]
    db_dir = base_dir / "data" / "faiss_index"
    
    db = FAISS.from_documents(chunks, embedding_function)
    db.save_local(str(db_dir))
    
    print(f"   ✅ Index sauvegardé dans : {db_dir}")
    
    # 5. Test rapide
    print(f"\n🔍 Test de recherche rapide...")
    test_queries = [
        "Comment justifier une absence?",
        "Horaires de cours",
        "Règlement informatique"
    ]
    
    for query in test_queries[:1]:  # Tester seulement la première
        results = db.similarity_search(query, k=2)
        print(f"   Q: '{query}'")
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            doc_type = doc.metadata.get('doc_type', 'Unknown')
            preview = doc.page_content[:150].replace('\n', ' ')
            print(f"      {i}. [{doc_type}] {source}: {preview}...")
    
    print("\n" + "="*70)
    print("✅ INDEXATION TERMINÉE AVEC SUCCÈS !")
    print("="*70)
    print(f"\nUtilisation :")
    print(f"  python school_assistant/chatbot/bot.py 'Votre question'")

if __name__ == "__main__":
    build_index()
