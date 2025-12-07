#!/usr/bin/env python3
"""
Scraper Google Drive avec compte de service (pas OAuth)
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleDriveScraper:
    """Scraper Google Drive avec compte de service"""
    
    FOLDER_2025_2026 = "1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB"
    FOLDER_ARCHIVES = "1ArnSC0QfJQmP2yeaej1mbPDJ30_zBCu-"
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, service_account_file: str = None):
        """Initialize with service account"""
        if service_account_file is None:
            service_account_file = Path(__file__).parent / 'service-account.json'
        
        self.service_account_file = service_account_file
        self.service = None
    
    def authenticate(self):
        """Authenticate with service account (NO BROWSER)"""
        print("🔑 Authentification avec compte de service...")
        print(f"   Fichier : {self.service_account_file}")
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(self.service_account_file),
                scopes=self.SCOPES
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            print("✅ Connecté à Google Drive API (sans navigateur)\n")
        
        except FileNotFoundError:
            print(f"❌ ERREUR : Fichier {self.service_account_file} introuvable!")
            print("   Vérifiez que service-account.json existe.")
            raise
        except Exception as e:
            print(f"❌ ERREUR d'authentification: {e}")
            raise
    
    def list_files_in_folder(self, folder_id: str, days: int = 30) -> List[Dict]:
        """List files in a folder"""
        if not self.service:
            self.authenticate()
        
        date_filter = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        
        print(f"📂 Dossier : {folder_id[:20]}...")
        
        try:
            query = f"'{folder_id}' in parents and trashed = false and modifiedTime > '{date_filter}'"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, createdTime, modifiedTime, webViewLink, size)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            print(f"   ✅ {len(files)} fichier(s) trouvé(s)\n")
            
            return files
        
        except Exception as e:
            print(f"   ❌ Erreur: {e}\n")
            import traceback
            traceback.print_exc()
            return []
    
    def get_recent_notes(self, days: int = 7) -> List[Dict]:
        """Get recent notes"""
        notes = []
        
        print("📋 DOSSIER : NOTES DE SERVICE 2025-2026")
        print("="*80)
        files_2025 = self.list_files_in_folder(self.FOLDER_2025_2026, days=days)
        
        for file in files_2025:
            notes.append({
                'titre': file['name'],
                'contenu': f"Document: {file['name']} ({file.get('mimeType', 'Unknown')})",
                'date_publication': file.get('modifiedTime', datetime.now().isoformat())[:10],
                'url': file.get('webViewLink', ''),
                'file_id': file['id'],
                'mime_type': file.get('mimeType'),
                'size': file.get('size', 0)
            })
            
            print(f"  📄 {file['name']}")
            print(f"     📅 {file.get('modifiedTime', 'N/A')[:10]}")
            print(f"     📎 {file.get('mimeType', 'N/A')}")
            print()
        
        print(f"📊 TOTAL : {len(notes)} note(s) récente(s)\n")
        
        return notes


if __name__ == "__main__":
    print("🚀 Scraper Google Drive (Compte de Service - SANS NAVIGATEUR)\n")
    
    try:
        scraper = GoogleDriveScraper()
        notes = scraper.get_recent_notes(days=30)
        
        print("\n" + "="*80)
        print("📋 RÉSUMÉ")
        print("="*80)
        
        if notes:
            for i, note in enumerate(notes, 1):
                print(f"\n{i}. {note['titre']}")
                print(f"   📅 {note['date_publication']}")
                print(f"   🔗 {note['url']}")
        else:
            print("\n⚠️ Aucune note trouvée.")
            print("   Vérifiez que:")
            print("   1. Le compte de service a accès aux dossiers")
            print("   2. Les dossiers contiennent des fichiers récents")
            print(f"   3. Email du compte: apm-notes-reader@apm-notes-service.iam.gserviceaccount.com")
    
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
