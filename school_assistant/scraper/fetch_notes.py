import os
from playwright.sync_api import sync_playwright
import datetime

def fetch_content():
    # Construct absolute path to auth file relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # school_assistant
    auth_file = os.path.join(base_dir, "auth", "state", "auth.json")
    
    # Check if auth file exists
    if not os.path.exists(auth_file):
        # Try relative path from execution root
        if os.path.exists("state/auth.json"):
            auth_file = "state/auth.json"
        else:
            print(f"ERREUR: Fichier d'authentification introuvable à : {auth_file}")
            print("Veuillez exécuter 'school_assistant/auth/login_setup.py' d'abord.")
            return

    print(f"Utilisation de la session : {auth_file}")

    with sync_playwright() as p:
        # Headless = True pour l'exécution quotidienne silencieuse
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(storage_state=auth_file)
            page = context.new_page()
            
            # URL spécifique des Notes de Service (trouvée dans le menu)
            url = "https://sites.google.com/eduhainaut.be/apm/notes-de-service"
            print(f"Connexion à {url}...")
            page.goto(url)
            page.wait_for_load_state("networkidle")
            
            # Extraction du texte
            content = page.evaluate("""() => {
                const textNodes = [];
                document.querySelectorAll('.tyJCtd').forEach(el => {
                    textNodes.push(el.innerText);
                });
                return textNodes.join('\\n\\n');
            }""")
            
            # Sauvegarder
            data_dir = os.path.join(base_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            filepath = os.path.join(data_dir, "notes_latest.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"Notes extraites : {len(content)} caractères. (Fichier: {filepath})")
            return content
            
        except Exception as e:
            print(f"Erreur lors du scan : {e}")
            return None
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_content()
