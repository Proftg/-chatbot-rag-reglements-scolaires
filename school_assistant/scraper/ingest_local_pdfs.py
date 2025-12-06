import os
from pathlib import Path
from pypdf import PdfReader

def ingest_pdfs(pdf_folder: Path, output_folder: Path) -> None:
    """Parcourt tous les *.pdf* du dossier `pdf_folder`, extrait le texte et le sauvegarde.
    Chaque PDF devient un fichier <nom>.txt dans `output_folder`.
    """
    if not pdf_folder.is_dir():
        raise FileNotFoundError(f"Le dossier PDF n’existe pas : {pdf_folder}")

    # Debug – afficher le contenu du dossier (utile avec les caractères accentués)
    print(f"[DEBUG] Dossier PDF recherché : {pdf_folder}")
    print("[DEBUG] Contenu du dossier :")
    for f in pdf_folder.iterdir():
        print(f"   - {f.name}")

    output_folder.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_folder.glob("*.pdf"):
        print(f"🔎 Extraction de {pdf_path.name}")
        try:
            reader = PdfReader(str(pdf_path))
            # concatène le texte de chaque page
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            txt_name = pdf_path.stem + ".txt"
            out_path = output_folder / txt_name
            out_path.write_text(text, encoding="utf-8")
            print(f"✅  → {out_path.name} ({len(text)} caractères)")
        except Exception as e:
            print(f"❌  Erreur sur {pdf_path.name} : {e}")

if __name__ == "__main__":
    # Chemin absolu du dossier contenant vos PDF (nom avec accent)
    pdf_dir = Path(__file__).resolve().parents[2] / "Réglements"
    # Dossier où le texte sera stocké (déjà utilisé par le RAG)
    data_dir = Path(__file__).resolve().parents[2] / "data"
    ingest_pdfs(pdf_dir, data_dir)
