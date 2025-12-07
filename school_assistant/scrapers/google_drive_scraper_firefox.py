#!/usr/bin/env python3
"""
Google Drive Scraper avec Playwright Firefox (authentification persistante)
La première fois, connectez-vous manuellement à Google
Les fois suivantes, l'authentification persiste automatiquement
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from typing import List, Dict
import time
import os

class GoogleDriveScraperFirefox:
    """Scraper pour Google Drive utilisant Firefox avec état persistant"""
    
    # Configuration
    BROWSER_STATE_DIR = os.path.expanduser('~/project/AMP/school_assistant/scrapers/.browser_state')
    
    # URLs des dossiers Google Drive
    FOLDER_2025_2026 = 'https://drive.google.com/drive/folders/1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB'
    FOLDER_ARCHIVES = 'https://drive.google.com/drive/folders/1ArnSC0QfJQmP2yeaej1mbPDJ30_zBCu-'
    
    def __init__(self, headless: bool = False):
        """
        Initialise le scraper
        Args:
            headless: Si True, mode invisible. Si False, mode visible (pour debug)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def start_browser(self) -> bool:
        """
        Démarre Firefox avec état persistant
        Returns:
            bool: True si succès, False sinon
        """
        try:
            print("🦊 Démarrage de Firefox...")
            print(f"   État sauvegardé dans : {self.BROWSER_STATE_DIR}")
            
            # Créer le dossier d'état s'il n'existe pas
            os.makedirs(self.BROWSER_STATE_DIR, exist_ok=True)
            
            self.playwright = sync_playwright().start()
            
            # Lancer Firefox avec contexte persistant
            self.browser = self.playwright.firefox.launch(
                headless=self.headless,
                args=['--no-sandbox']
            )
            
            # Créer un contexte avec état persistant
            self.context = self.browser.new_context(
                storage_state=os.path.join(self.BROWSER_STATE_DIR, 'state.json') 
                    if os.path.exists(os.path.join(self.BROWSER_STATE_DIR, 'state.json')) 
                    else None
            )
            
            self.page = self.context.new_page()
            
            print("✅ Firefox démarré")
            
            # Vérifier si on est authentifié
            if not self.check_authentication():
                print("\n⚠️  PREMIÈRE UTILISATION : Authentification requise")
                print("   1. Une fenêtre Firefox va s'ouvrir")
                print("   2. Connectez-vous à votre compte Google")
                print("   3. Accédez à Google Drive")
                print("   4. Appuyez sur Entrée ici quand c'est fait")
                
                self.manual_authentication()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage Firefox: {e}")
            return False
    
    def check_authentication(self) -> bool:
        """
        Vérifie si l'utilisateur est déjà authentifié sur Google
        Returns:
            bool: True si authentifié, False sinon
        """
        try:
            self.page.goto('https://drive.google.com', timeout=10000)
            time.sleep(3)
            
            # Si on est redirigé vers la page de login, pas authentifié
            if 'accounts.google.com' in self.page.url:
                return False
            
            # Si on voit "Mon Drive", on est authentifié
            if 'drive.google.com' in self.page.url:
                print("✅ Déjà authentifié à Google Drive")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Erreur vérification auth: {e}")
            return False
    
    def manual_authentication(self):
        """Permet à l'utilisateur de s'authentifier manuellement"""
        try:
            # Ouvrir Google Drive
            self.page.goto('https://drive.google.com')
            
            # Attendre que l'utilisateur se connecte
            input("\n👉 Connectez-vous à Google Drive dans la fenêtre Firefox, puis appuyez sur ENTRÉE ici...")
            
            # Sauvegarder l'état d'authentification
            self.context.storage_state(path=os.path.join(self.BROWSER_STATE_DIR, 'state.json'))
            print("✅ État d'authentification sauvegardé pour les prochaines fois")
            
        except Exception as e:
            print(f"❌ Erreur authentification manuelle: {e}")
    
    def list_folder_contents(self, folder_url: str, folder_name: str, days_back: int = 7) -> List[Dict]:
        """
        Liste le contenu d'un dossier Google Drive
        """
        try:
            print(f"\n📂 Navigation vers {folder_name}...")
            self.page.goto(folder_url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Passer en vue liste pour extraction plus facile
            try:
                self.page.click('[aria-label*="Affichage Liste"]', timeout=5000)
                time.sleep(1)
            except:
                pass  # Déjà en vue liste
            
            # Extraire les fichiers visibles
            files = []
            
            # Sélecteur pour les lignes de fichiers/dossiers
            rows = self.page.query_selector_all('[data-id]')
            
            print(f"   📄 {len(rows)} élément(s) détecté(s)")
            
            for row in rows:
                try:
                    # Extraire les informations
                    file_id = row.get_attribute('data-id')
                    
                    # Nom du fichier
                    name_elem = row.query_selector('[data-tooltip]')
                    name = name_elem.get_attribute('data-tooltip') if name_elem else ""
                    
                    if not name or not file_id:
                        continue
                    
                    # Type (dossier ou fichier)
                    type_attr = row.get_attribute('data-type')
                    is_folder = type_attr == 'folder' or 'Dossier' in name
                    
                    if is_folder:
                        continue  # Ignorer les dossiers pour l'instant
                    
                    # Créer l'entrée
                    file_info = {
                        'file_id': file_id,
                        'titre': name.strip(),
                        'contenu': f"Document Google Drive: {name}",
                        'date_publication': datetime.now().isoformat(),
                        'url': f"https://drive.google.com/file/d/{file_id}/view",
                        'mime_type': 'application/octet-stream',
                        'size': 0
                    }
                    
                    files.append(file_info)
                    print(f"      ✓ {name[:50]}")
                    
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(files)} fichier(s) extrait(s)")
            return files
            
        except Exception as e:
            print(f"❌ Erreur listing {folder_name}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_recent_notes(self, days_back: int = 7) -> List[Dict]:
        """Récupère les notes récentes des deux dossiers"""
        if not self.start_browser():
            return []
        
        all_notes = []
        
        try:
            # Dossier 1
            print("\n📋 DOSSIER : NOTES DE SERVICE 2025-2026")
            print("=" * 80)
            notes_2025 = self.list_folder_contents(
                self.FOLDER_2025_2026, 
                "NS 25-26",
                days_back
            )
            all_notes.extend(notes_2025)
            
            # Dossier 2
            print("\n📋 DOSSIER : ARCHIVES")
            print("=" * 80)
            notes_archives = self.list_folder_contents(
                self.FOLDER_ARCHIVES,
                "Archives", 
                days_back
            )
            all_notes.extend(notes_archives)
            
            print(f"\n📊 TOTAL : {len(all_notes)} note(s)")
            
        finally:
            self.close()
        
        return all_notes
    
    def close(self):
        """Ferme le navigateur"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("\n✅ Firefox fermé")
        except Exception as e:
            print(f"⚠️  Erreur fermeture: {e}")


def main():
    """Fonction principale de test"""
    print("🚀 Scraper Google Drive (Firefox avec authentification persistante)")
    print("=" * 80)
    
    # Mode visible pour le premier test
    scraper = GoogleDriveScraperFirefox(headless=False)
    notes = scraper.get_recent_notes(days_back=30)
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ")
    print("=" * 80)
    
    if notes:
        print(f"✅ {len(notes)} note(s) récupérée(s):\n")
        for i, note in enumerate(notes[:10], 1):
            print(f"{i}. {note['titre']}")
            if note['url']:
                print(f"   🔗 {note['url'][:60]}...")
            print()
    else:
        print("⚠️ Aucune note trouvée")


if __name__ == '__main__':
    main()
