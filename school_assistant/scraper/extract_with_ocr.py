#!/usr/bin/env python3
"""
Script d'extraction OCR pour les PDFs scannés
Utilise Tesseract OCR pour extraire le texte des images
"""
import os
from pathlib import Path
from pypdf import PdfReader
import subprocess
import sys

# Vérifier si les dépendances OCR sont installées
def check_dependencies():
    """Vérifie que Tesseract et les bibliothèques sont installées."""
    print("🔍 Vérification des dépendances OCR...")
    
    # Vérifier Tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Tesseract OCR installé")
        else:
            print("   ❌ Tesseract non trouvé")
            return False
    except FileNotFoundError:
        print("   ❌ Tesseract non installé")
        print("\n📥 Installation requise :")
        print("   sudo apt update")
        print("   sudo apt install tesseract-ocr tesseract-ocr-fra")
        print("   pip install pytesseract pdf2image --break-system-packages")
        return False
    
    # Vérifier les modules Python
    try:
        import pytesseract
        print("   ✅ pytesseract installé")
    except ImportError:
        print("   ❌ pytesseract non installé")
        print("   pip install pytesseract --break-system-packages")
        return False
    
    try:
        import pdf2image
        print("   ✅ pdf2image installé")
    except ImportError:
        print("   ❌ pdf2image non installé")
        print("   pip install pdf2image --break-system-packages")
        return False
    
    return True


def extract_with_ocr(pdf_path: Path) -> str:
    """Extrait le texte d'un PDF scanné via OCR."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        
        print(f"   📸 Conversion en images...")
        images = convert_from_path(str(pdf_path))
        
        text = ""
        total_pages = len(images)
        
        for i, image in enumerate(images, 1):
            print(f"   🔤 OCR page {i}/{total_pages}...", end='\r')
            page_text = pytesseract.image_to_string(image, lang='fra')
            text += page_text + "\n\n"
        
        print(f"   ✅ OCR terminé ({total_pages} pages)")
        return text.strip()
        
    except Exception as e:
        print(f"   ❌ Erreur OCR : {e}")
        return ""


def process_empty_pdfs():
    """Traite les PDFs qui n'ont pas pu être extraits normalement."""
    base_dir = Path(__file__).resolve().parents[1]
    pdf_dir = base_dir / "Réglements"
    data_dir = base_dir / "data"
    
    # PDFs identifiés comme vides/scannés
    problematic_pdfs = [
        "Règlement atelier.pdf",
        "Projet éducatif et pédagogique Province de Hainaut.pdf",
        "Dress code - Section Coiffeur.pdf",
        "Règlement éducation physique.pdf",
        "Règlement de Travail - juillet 2024.pdf"
    ]
    
    print(f"\n📂 Traitement des PDFs scannés...")
    print(f"   Source : {pdf_dir}")
    print(f"   Destination : {data_dir}\n")
    
    success_count = 0
    
    for pdf_name in problematic_pdfs:
        pdf_path = pdf_dir / pdf_name
        
        if not pdf_path.exists():
            print(f"⚠️  {pdf_name} - Fichier non trouvé")
            continue
        
        print(f"🔍 Traitement : {pdf_name}")
        
        # Vérifier d'abord l'extraction classique
        try:
            reader = PdfReader(str(pdf_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            
            if len(text.strip()) > 100:
                print(f"   ℹ️  Extraction classique suffisante ({len(text)} caractères)")
                txt_name = pdf_path.stem + ".txt"
                output_path = data_dir / txt_name
                output_path.write_text(text, encoding='utf-8')
                success_count += 1
                continue
        except Exception as e:
            print(f"   ⚠️  Extraction classique échouée : {e}")
        
        # OCR nécessaire
        text = extract_with_ocr(pdf_path)
        
        if len(text) < 100:
            print(f"   ❌ OCR insuffisant ({len(text)} caractères)")
            continue
        
        # Sauvegarder
        txt_name = pdf_path.stem + ".txt"
        output_path = data_dir / txt_name
        output_path.write_text(text, encoding='utf-8')
        
        print(f"   ✅ Sauvegardé : {txt_name} ({len(text):,} caractères)")
        success_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Traitement terminé : {success_count}/{len(problematic_pdfs)} PDFs extraits")
    print(f"{'='*70}")
    
    if success_count > 0:
        print("\n💡 Prochaine étape : Reconstruire l'index RAG")
        print("   python school_assistant/chatbot/setup_rag.py")


if __name__ == "__main__":
    print("="*70)
    print("   EXTRACTION OCR DES PDFs SCANNÉS")
    print("="*70 + "\n")
    
    if not check_dependencies():
        print("\n❌ Dépendances manquantes. Installation requise.")
        sys.exit(1)
    
    process_empty_pdfs()
