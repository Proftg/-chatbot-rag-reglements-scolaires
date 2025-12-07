#!/usr/bin/env python3
"""
Google Drive Scraper avec Playwright (utilise le profil Chrome authentifié)
Scrape les notes de service depuis Google Drive sans API
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re

class GoogleDriveScraperPlaywright:
    """Scraper pour Google Drive utilisant Playwright avec profil Chrome"""
    
    # Configuration
    CHROME_USER_DATA = '/mnt/c/Users/tahar/AppData/Local/Google/Chrome/User Data'
    CHROME_PROFILE = 'Default'
    
    # URLs des dossiers Google Drive
    FOLDER_2025_2026 = 'https://drive.google.com/drive/folders/1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB'
    FOLDER_ARCHIVES = 'https://drive.google.com/drive/folders/1ArnSC0QfJQmP2yeaej1mbPDJ30_zBCu-'
    
    def __init__(self):
        """Initialise le scraper"""
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def start_browser(self) -> bool:
        """
        Démarre Chrome avec le profil utilisateur authentifié
        Returns:
            bool: True si succès, False sinon
        """
        try:
            print("🌐 Démarrage de Chrome avec profil authentifié...")
            print(f"   Profil : {self.CHROME_USER_DATA}/{self.CHROME_PROFILE}")
            
            self.playwright = sync_playwright().start()
            
            # Lancer Chrome avec le profil utilisateur
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.CHROME_USER_DATA,
                headless=False,  # Mode visible pour debug
                channel='chrome',
                args=[
                    f'--profile-directory={self.CHROME_PROFILE}',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            print("✅ Chrome démarré avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage Chrome: {e}")
            return False
    
    def list_folder_contents(self, folder_url: str, days_back: int = 7) -> List[Dict]:
        """
        Liste le contenu d'un dossier Google Drive
        Args:
            folder_url: URL du dossier Google Drive
            days_back: Nombre de jours en arrière pour filtrer
        Returns:
            Liste de dictionnaires contenant les infos des fichiers
        """
        try:
            print(f"\n📂 Navigation vers : {folder_url[:50]}...")
            self.page.goto(folder_url, wait_until='networkidle', timeout=30000)
            
            # Attendre que la page Google Drive charge
            time.sleep(3)
            
            # Vérifier si on est bien sur Google Drive
            if "drive.google.com" not in self.page.url:
                print("❌ Pas sur Google Drive - possible problème d'authentification")
                return []
            
            print("✅ Page Google Drive chargée")
            
            # Chercher tous les dossiers (sous-dossiers mois)
            subfolders = self.get_subfolders()
            
            all_files = []
            
            if subfolders:
                print(f"📁 {len(subfolders)} sous-dossier(s) trouvé(s)")
                
                for subfolder in subfolders:
                    print(f"   └─ Exploration : {subfolder['name']}")
                    
                    # Cliquer sur le sous-dossier
                    self.page.click(f'text="{subfolder["name"]}"')
                    time.sleep(2)
                    
                    # Extraire les fichiers
                    files = self.extract_files_from_current_view(days_back)
                    all_files.extend(files)
                    
                    # Revenir au dossier parent
                    self.page.go_back()
                    time.sleep(2)
            else:
                # Pas de sous-dossiers, extraire directement
                print("📄 Extraction des fichiers du dossier actuel...")
                files = self.extract_files_from_current_view(days_back)
                all_files.extend(files)
            
            print(f"✅ {len(all_files)} fichier(s) trouvé(s)")
            return all_files
            
        except Exception as e:
            print(f"❌ Erreur lors du listing : {e}")
            return []
    
    def get_subfolders(self) -> List[Dict]:
        """
        Récupère la liste des sous-dossiers visibles
        Returns:
            Liste de dictionnaires avec nom et sélecteur des dossiers
        """
        try:
            # Sélecteurs possibles pour les dossiers dans Google Drive
            folder_selectors = [
                '[data-target="doc"][data-type="folder"]',
                '.a-s-tb-ec-T',  # Ancien sélecteur
                '[role="button"][aria-label*="Dossier"]'
            ]
            
            folders = []
            
            for selector in folder_selectors:
                elements = self.page.query_selector_all(selector)
                if elements:
                    for elem in elements:
                        name = elem.get_attribute('aria-label') or elem.inner_text()
                        if name:
                            folders.append({'name': name.strip(), 'element': elem})
                    break
            
            return folders
            
        except Exception as e:
            print(f"⚠️  Erreur get_subfolders: {e}")
            return []
    
    def extract_files_from_current_view(self, days_back: int = 7) -> List[Dict]:
        """
        Extrait les fichiers de la vue actuelle
        Args:
            days_back: Filtre par nombre de jours
        Returns:
            Liste de fichiers
        """
        try:
            files = []
            date_limite = datetime.now() - timedelta(days=days_back)
            
            # Attendre que les fichiers se chargent
            time.sleep(2)
            
            # Sélecteurs pour les fichiers
            file_selectors = [
                '[data-target="doc"]:not([data-type="folder"])',
                '.a-s-tb-ec-D',
            ]
            
            file_elements = []
            for selector in file_selectors:
                file_elements = self.page.query_selector_all(selector)
                if file_elements:
                    break
            
            print(f"   📄 {len(file_elements)} élément(s) détecté(s)")
            
            for elem in file_elements:
                try:
                    # Extraire le nom du fichier
                    name = elem.get_attribute('aria-label') or elem.inner_text()
                    
                    if not name:
                        continue
                    
                    # Extraire l'URL (si disponible)
                    file_id = elem.get_attribute('data-id')
                    url = f"https://drive.google.com/file/d/{file_id}/view" if file_id else ""
                    
                    # Pour l'instant, on prend tous les fichiers (filtrage par date après)
                    file_info = {
                        'file_id': file_id or '',
                        'titre': name.strip(),
                        'contenu': f"Document Google Drive: {name}",
                        'date_publication': datetime.now().isoformat(),  # À améliorer
                        'url': url,
                        'mime_type': 'application/vnd.google-apps.document',
                        'size': 0
                    }
                    
                    files.append(file_info)
                    
                except Exception as e:
                    print(f"      ⚠️  Erreur extraction fichier: {e}")
                    continue
            
            return files
            
        except Exception as e:
            print(f"❌ Erreur extract_files: {e}")
            return []
    
    def get_recent_notes(self, days_back: int = 7) -> List[Dict]:
        """
        Récupère les notes récentes des deux dossiers
        Args:
            days_back: Nombre de jours en arrière
        Returns:
            Liste combinée des notes récentes
        """
        if not self.start_browser():
            return []
        
        all_notes = []
        
        try:
            # Dossier 1: Notes de service 2025-2026
            print("\n📋 DOSSIER : NOTES DE SERVICE 2025-2026")
            print("=" * 80)
            notes_2025 = self.list_folder_contents(self.FOLDER_2025_2026, days_back)
            all_notes.extend(notes_2025)
            
            # Dossier 2: Archives
            print("\n📋 DOSSIER : ARCHIVES")
            print("=" * 80)
            notes_archives = self.list_folder_contents(self.FOLDER_ARCHIVES, days_back)
            all_notes.extend(notes_archives)
            
            print(f"\n📊 TOTAL : {len(all_notes)} note(s) récente(s)")
            
        finally:
            self.close()
        
        return all_notes
    
    def close(self):
        """Ferme le navigateur"""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            print("\n✅ Navigateur fermé")
        except Exception as e:
            print(f"⚠️  Erreur fermeture: {e}")


def main():
    """Fonction principale de test"""
    print("🚀 Scraper Google Drive (Playwright avec profil Chrome)")
    
    scraper = GoogleDriveScraperPlaywright()
    notes = scraper.get_recent_notes(days_back=30)  # 30 jours pour test
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ")
    print("=" * 80)
    
    if notes:
        print(f"✅ {len(notes)} note(s) récupérée(s):\n")
        for i, note in enumerate(notes[:10], 1):  # Afficher les 10 premières
            print(f"{i}. {note['titre']}")
            print(f"   🔗 {note['url']}")
            print()
    else:
        print("⚠️ Aucune note trouvée.")
        print("   Vérifiez que:")
        print("   1. Chrome est bien connecté à votre compte Google")
        print("   2. Vous avez accès aux dossiers")


if __name__ == '__main__':
    main()
