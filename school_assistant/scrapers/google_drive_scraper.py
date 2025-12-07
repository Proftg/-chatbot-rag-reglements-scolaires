#!/usr/bin/env python3
"""
Google Drive Scraper avec Service Account
Récupère les notes de service depuis Google Drive (SANS NAVIGATEUR)
Version avec exploration récursive des sous-dossiers
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys

class GoogleDriveScraper:
    """Scraper pour Google Drive utilisant un compte de service"""
    
    # Configuration
    SERVICE_ACCOUNT_FILE = '/home/tahar/project/AMP/school_assistant/scrapers/service-account.json'
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # IDs des dossiers Google Drive
    FOLDER_2025_2026 = '1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB'
    FOLDER_ARCHIVES = '1ArnSC0QfJQmP2yeaej1mbPDJ30_zBCu-'
    
    def __init__(self):
        """Initialise le scraper"""
        self.service = None
        self.credentials = None
    
    def authenticate(self) -> bool:
        """
        Authentifie avec Google Drive via compte de service
        Returns:
            bool: True si succès, False sinon
        """
        try:
            print("🔑 Authentification avec compte de service...")
            print(f"   Fichier : {self.SERVICE_ACCOUNT_FILE}")
            
            self.credentials = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE,
                scopes=self.SCOPES
            )
            
            self.service = build('drive', 'v3', credentials=self.credentials)
            print("✅ Connecté à Google Drive API (sans navigateur)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur d'authentification: {e}")
            return False
    
    def list_all_folders_recursive(self, parent_folder_id: str, indent: int = 0) -> List[str]:
        """
        Liste récursivement tous les sous-dossiers
        Args:
            parent_folder_id: ID du dossier parent
            indent: Niveau d'indentation pour l'affichage
        Returns:
            Liste des IDs de tous les dossiers trouvés
        """
        all_folder_ids = [parent_folder_id]
        
        try:
            # Chercher tous les sous-dossiers directs
            query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name)",
                pageSize=100
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                prefix = "  " * indent
                print(f"{prefix}📁 {len(folders)} sous-dossier(s) trouvé(s)")
                
                for folder in folders:
                    print(f"{prefix}   └─ {folder['name']} (ID: {folder['id'][:20]}...)")
                    all_folder_ids.append(folder['id'])
                    
                    # Récursion pour explorer les sous-sous-dossiers
                    sub_folders = self.list_all_folders_recursive(folder['id'], indent + 2)
                    all_folder_ids.extend(sub_folders[1:])  # Exclure le dossier lui-même
            
            return all_folder_ids
            
        except HttpError as error:
            print(f"❌ Erreur lors de la liste des dossiers: {error}")
            return all_folder_ids
    
    def list_files_in_folder(self, folder_id: str, days_back: int = 7) -> List[Dict]:
        """
        Liste tous les fichiers dans un dossier (non récursif)
        Args:
            folder_id: ID du dossier Google Drive
            days_back: Nombre de jours en arrière pour filtrer
        Returns:
            Liste de dictionnaires contenant les infos des fichiers
        """
        try:
            # Date limite (X jours en arrière)
            date_limite = datetime.now() - timedelta(days=days_back)
            date_limite_str = date_limite.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Requête : fichiers modifiés après date_limite, non-dossiers, non-supprimés
            query = (
                f"'{folder_id}' in parents "
                f"and modifiedTime > '{date_limite_str}' "
                f"and mimeType != 'application/vnd.google-apps.folder' "
                f"and trashed = false"
            )
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, modifiedTime, webViewLink, size)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            # Transformer en format standardisé
            notes = []
            for file in files:
                note = {
                    'file_id': file['id'],
                    'titre': file['name'],
                    'contenu': f"Document Google Drive: {file['name']}",
                    'date_publication': file.get('modifiedTime', ''),
                    'url': file.get('webViewLink', ''),
                    'mime_type': file.get('mimeType', ''),
                    'size': file.get('size', 0)
                }
                notes.append(note)
            
            return notes
            
        except HttpError as error:
            print(f"❌ Erreur API Google Drive: {error}")
            return []
    
    def get_recent_notes(self, days_back: int = 7) -> List[Dict]:
        """
        Récupère les notes récentes des deux dossiers (avec exploration récursive)
        Args:
            days_back: Nombre de jours en arrière
        Returns:
            Liste combinée des notes récentes
        """
        if not self.authenticate():
            return []
        
        all_notes = []
        
        # Dossier 1: Notes de service 2025-2026
        print("\n📋 DOSSIER : NOTES DE SERVICE 2025-2026")
        print("=" * 80)
        print(f"📂 Exploration récursive du dossier {self.FOLDER_2025_2026[:20]}...")
        
        folder_ids_2025 = self.list_all_folders_recursive(self.FOLDER_2025_2026)
        print(f"\n📊 Total de {len(folder_ids_2025)} dossier(s) à explorer")
        
        for folder_id in folder_ids_2025:
            notes = self.list_files_in_folder(folder_id, days_back)
            if notes:
                print(f"   ✅ {len(notes)} fichier(s) trouvé(s) dans {folder_id[:20]}...")
                all_notes.extend(notes)
        
        # Dossier 2: Archives
        print("\n📋 DOSSIER : ARCHIVES")
        print("=" * 80)
        print(f"📂 Exploration récursive du dossier {self.FOLDER_ARCHIVES[:20]}...")
        
        folder_ids_archives = self.list_all_folders_recursive(self.FOLDER_ARCHIVES)
        print(f"\n📊 Total de {len(folder_ids_archives)} dossier(s) à explorer")
        
        for folder_id in folder_ids_archives:
            notes = self.list_files_in_folder(folder_id, days_back)
            if notes:
                print(f"   ✅ {len(notes)} fichier(s) trouvé(s) dans {folder_id[:20]}...")
                all_notes.extend(notes)
        
        print(f"\n📊 TOTAL : {len(all_notes)} note(s) récente(s)")
        return all_notes


def main():
    """Fonction principale de test"""
    print("🚀 Scraper Google Drive (Compte de Service - SANS NAVIGATEUR)")
    
    scraper = GoogleDriveScraper()
    notes = scraper.get_recent_notes(days_back=30)  # 30 jours pour test
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ")
    print("=" * 80)
    
    if notes:
        print(f"✅ {len(notes)} note(s) récupérée(s):\n")
        for i, note in enumerate(notes[:5], 1):  # Afficher les 5 premières
            print(f"{i}. {note['titre']}")
            print(f"   📅 {note['date_publication']}")
            print(f"   🔗 {note['url']}")
            print()
    else:
        print("⚠️ Aucune note trouvée.")
        print("   Vérifiez que:")
        print("   1. Le compte de service a accès aux dossiers")
        print("   2. Les dossiers contiennent des fichiers récents")
        print(f"   3. Email du compte: {scraper.credentials.service_account_email}")


if __name__ == '__main__':
    main()
