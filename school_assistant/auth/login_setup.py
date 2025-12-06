import os
import time
from playwright.sync_api import sync_playwright

def login_and_save_state():
    # Determine absolute path for state storage
    current_dir = os.path.dirname(os.path.abspath(__file__))
    state_dir = os.path.join(current_dir, "state")
    
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)
        
    auth_file = os.path.join(state_dir, "auth.json")
    
    print("--- ASSISTANT CONFIGURATION ---")
    print(f"Stockage de la session dans : {auth_file}")
    print("1. Une fenêtre de navigateur va s'ouvrir.")
    print("2. Connectez-vous avec vos identifiants Google.")
    print("3. Une fois que vous voyez la page d'accueil de l'école (Notes de service/Règlement), revenez ici.")
    
    with sync_playwright() as p:
        # Launch browser in HEADED mode so user can see and type
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Ouverture du navigateur en cours...")
        
        # Navigate to the target site
        try:
            page.goto("https://sites.google.com/eduhainaut.be/apm/accueil")
        except Exception as e:
            print(f"Erreur lors du chargement initial (peut être ignorée si vous êtes redirigé): {e}")

        # Wait for user confirmation
        input("\n>>> Une fois connecté et sur la page d'accueil, appuyez sur ENTRÉE pour sauvegarder... <<<")
        
        # Save state
        context.storage_state(path=auth_file)
        print(f"Succès ! Session sauvegardée dans {auth_file}")
        print("Le script d'extraction pourra maintenant accéder au site.")
        
        browser.close()

if __name__ == "__main__":
    login_and_save_state()
