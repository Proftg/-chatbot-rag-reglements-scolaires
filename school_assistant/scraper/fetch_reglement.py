import os
import re
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
from io import BytesIO

def fetch_reglement():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_file = os.path.join(base_dir, "auth", "state", "auth.json")
    data_dir = os.path.join(base_dir, "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    print(f"Utilisation de la session : {auth_file}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(storage_state=auth_file)
            page = context.new_page()
            
            # 1. Récupérer l'URL du Padlet depuis la page Règlement
            url_main = "https://sites.google.com/eduhainaut.be/apm/outils-enseignant/reglements"
            print(f"Connexion à {url_main}...")
            page.goto(url_main)
            page.wait_for_load_state("networkidle")
            
            main_html = page.content()
            padlet_match = re.search(r'(https://padlet\.com/embed/[a-zA-Z0-9]+)', main_html)
            
            final_content = ""

            if padlet_match:
                padlet_url = padlet_match.group(1)
                print(f"Padlet détecté : {padlet_url}")
                
                print("Navigation vers le Padlet...")
                page.goto(padlet_url)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(5000) # Laisser le temps au JS de Padlet
                
                padlet_html = page.content()
                
                # Récupérer texte visible
                visible_text = page.evaluate("document.body.innerText")
                final_content += f"=== TEXTE VISIBLE SUR PADLET ===\n{visible_text}\n\n"
                
                # Chercher TOUS les liens (via Regex pour être sûr) dans tout le code source
                # Cela permet de trouver les liens 'cachés' dans le JSON ou le Shadow DOM
                print("Recherche des PDF...")
                # Liens .pdf
                links = re.findall(r'(https?://[^"\'<>\s]+\.pdf)', padlet_html, re.IGNORECASE)
                # Liens Padlet /file/
                links += re.findall(r'(https?://padlet\.com/[^"\'<>\s]+/file/[^"\'<>\s]+)', padlet_html, re.IGNORECASE)
                
                clean_links = list(set(links))
                print(f"  -> {len(clean_links)} documents PDF trouvés.")
                
                for link in clean_links:
                    try:
                        # Filtrer les liens non pertinents (images, styles...)
                        if not (".pdf" in link.lower() or "/file/" in link):
                            continue
                            
                        print(f"  -> Téléchargement de {link[:60]}...")
                        response = page.context.request.get(link)
                        
                        if response.status == 200:
                            body = response.body()
                            f = BytesIO(body)
                            
                            try:
                                reader = PdfReader(f)
                                text = ""
                                for page_num in range(len(reader.pages)):
                                    text += reader.pages[page_num].extract_text() + "\n"
                                
                                if len(text.strip()) > 50: # Garder si on a extrait du texte
                                    print(f"     ✅ Extrait {len(text)} caractères.")
                                    final_content += f"\n=== CONTENU DU DOCUMENT PDF: {link} ===\n{text}\n"
                                else:
                                    print("     ⚠️ PDF vide ou illisible (image ?).")
                            except Exception as pdf_err:
                                print(f"     ❌ Fichier non valide (pas un PDF?) : {pdf_err}")
                        else:
                            print(f"     ❌ Échec téléchargement (Status {response.status})")
                            
                    except Exception as e:
                        print(f"     ❌ Erreur globale sur ce lien: {e}")

            else:
                print("Pas de Padlet trouvé.")
            
            output_file = os.path.join(data_dir, "reglement_raw.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_content)
                
            print(f"Extraction terminée. Total: {len(final_content)} caractères.")
            
        except Exception as e:
            print(f"Erreur globale : {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_reglement()
