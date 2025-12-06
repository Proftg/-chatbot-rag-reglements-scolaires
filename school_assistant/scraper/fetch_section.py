import os
import re
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
from io import BytesIO

def fetch_section(url: str, output_name: str, auth_file: str = None) -> str:
    """Fetch a Google Site section (e.g., Reglements, Documents Utiles).
    - Navigates to the provided URL (requires authentication via ``auth_file``).
    - Extracts visible text.
    - Finds any PDF links (including Padlet embedded PDFs) and extracts their text.
    - Saves the combined content to ``data/<output_name>.txt``.
    Returns the path of the created file.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    output_path = os.path.join(data_dir, f"{output_name}.txt")
    
    # Utiliser le même fichier d'authentification que les autres scrapers
    if auth_file is None:
        auth_file = os.path.join(base_dir, "auth", "state", "auth.json")
    
    print(f"[fetch_section] Chargement de {url} (auth={auth_file})")
    final_content = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(storage_state=auth_file)
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            
            # Texte visible
            visible_text = page.evaluate("document.body.innerText")
            final_content += f"=== TEXTE VISIBLE ({output_name}) ===\n{visible_text}\n\n"
            
            # Recherche de PDF via regex sur le HTML complet (inclut les liens dans les iframes, etc.)
            html = page.content()
            pdf_links = re.findall(r'(https?://[^"\'<>\s]+\.pdf)', html, re.IGNORECASE)
            # Padlet file links (souvent /file/)
            pdf_links += re.findall(r'(https?://padlet\.com/[^"\'<>\s]+/file/[^"\'<>\s]+)', html, re.IGNORECASE)
            pdf_links = list(set(pdf_links))
            print(f"[fetch_section] {len(pdf_links)} PDF(s) détectés.")
            
            for link in pdf_links:
                try:
                    print(f"[fetch_section] Téléchargement de {link[:60]}...")
                    response = page.context.request.get(link)
                    if response.status == 200:
                        body = response.body()
                        f = BytesIO(body)
                        try:
                            reader = PdfReader(f)
                            text = ""
                            for p in range(len(reader.pages)):
                                text += reader.pages[p].extract_text() or ""
                            if text.strip():
                                final_content += f"=== CONTENU PDF ({link}) ===\n{text}\n\n"
                                print(f"[fetch_section] PDF extrait ({len(text)} caractères).")
                            else:
                                print("[fetch_section] PDF vide ou non textuel.")
                        except Exception as pdf_err:
                            print(f"[fetch_section] Erreur lecture PDF : {pdf_err}")
                    else:
                        print(f"[fetch_section] Échec téléchargement (status {response.status})")
                except Exception as e:
                    print(f"[fetch_section] Erreur lors du traitement du lien {link}: {e}")
        except Exception as e:
            print(f"[fetch_section] Erreur globale : {e}")
        finally:
            browser.close()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    print(f"[fetch_section] Sauvegarde terminée : {output_path} ({len(final_content)} caractères)")
    return output_path

if __name__ == "__main__":
    # Exemple d'utilisation rapide (à remplacer par vos URLs)
    # fetch_section("https://sites.google.com/eduhainaut.be/apm/outils-enseignant/reglements", "reglements")
    pass
