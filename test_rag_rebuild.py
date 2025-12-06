#!/usr/bin/env python3
"""
Script de test pour reconstruire l'index RAG avec les PDFs locaux
"""
import os
from pathlib import Path
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
import re

def preprocess_text(text: str) -> str:
    """Nettoie le texte extrait."""
    # Suppression des métadonnées web
    text = re.sub(r'(likes|comments|add comment|share|skip to content)', '', text, flags=re.IGNORECASE)
    # Normalisation des espaces
    text = re.sub(r'\s+', ' ', text)
    # Normalisation des sauts de ligne
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_pdfs():
    """Extrait et charge tous les PDFs depuis le dossier Réglements."""
    pdf_dir = Path("/home/tahar/project/AMP/Réglements")
    documents = []
    
    print(f"📂 Scan du dossier : {pdf_dir}")
    print(f"   Nombre de fichiers : {len(list(pdf_dir.glob('*.[pP][dD][fF]')))}\n")
    
    for pdf_path in pdf_dir.glob("*.[pP][dD][fF]"):  # Support .pdf et .PDF
        print(f"🔍 Traitement : {pdf_path.name}")
        try:
            reader = PdfReader(str(pdf_path))
            total_text = ""
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                total_text += text + "\n"
            
            # Nettoyage
            clean_text = preprocess_text(total_text)
            
            if len(clean_text) < 100:
                print(f"   ⚠️  PDF vide ou scanné (seulement {len(clean_text)} caractères)")
                continue
                
            documents.append(Document(
                page_content=clean_text,
                metadata={
                    "source": pdf_path.name,
                    "num_pages": len(reader.pages),
                    "char_count": len(clean_text)
                }
            ))
            
            print(f"   ✅ {len(reader.pages)} pages, {len(clean_text)} caractères")
            
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
    
    return documents

def build_rag_index(documents):
    """Construit l'index RAG avec chunking optimisé."""
    print(f"\n📊 Découpage en chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"   ✅ {len(chunks)} chunks créés")
    
    # Afficher quelques statistiques
    chunk_sizes = [len(chunk.page_content) for chunk in chunks]
    print(f"   📏 Taille moyenne : {sum(chunk_sizes) // len(chunk_sizes)} caractères")
    print(f"   📏 Min: {min(chunk_sizes)}, Max: {max(chunk_sizes)}")
    
    print(f"\n🧠 Calcul des embeddings avec all-MiniLM-L6-v2...")
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print(f"💾 Construction de l'index FAISS...")
    db = FAISS.from_documents(chunks, embedding_function)
    
    output_dir = Path("/home/tahar/project/AMP/school_assistant/data/faiss_index_new")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    db.save_local(str(output_dir))
    print(f"   ✅ Index sauvegardé dans : {output_dir}")
    
    return db

def test_search(db):
    """Test de recherche."""
    print(f"\n🔍 Test de recherche...")
    
    queries = [
        "Comment justifier une absence?",
        "Quels sont les horaires de cours?",
        "Règlement informatique",
    ]
    
    for query in queries:
        print(f"\n   Q: {query}")
        docs = db.similarity_search(query, k=2)
        for i, doc in enumerate(docs, 1):
            preview = doc.page_content[:200].replace('\n', ' ')
            print(f"      {i}. [{doc.metadata['source']}] {preview}...")

if __name__ == "__main__":
    print("="*70)
    print("   TEST DE RECONSTRUCTION DE L'INDEX RAG")
    print("="*70 + "\n")
    
    # Étape 1 : Extraction
    documents = extract_pdfs()
    
    if not documents:
        print("\n❌ ERREUR : Aucun document valide extrait !")
        exit(1)
    
    print(f"\n📚 Total : {len(documents)} documents extraits")
    total_chars = sum(len(doc.page_content) for doc in documents)
    print(f"   📝 {total_chars:,} caractères au total")
    
    # Étape 2 : Construction RAG
    db = build_rag_index(documents)
    
    # Étape 3 : Test
    test_search(db)
    
    print("\n" + "="*70)
    print("✅ RECONSTRUCTION TERMINÉE !")
    print("="*70)
