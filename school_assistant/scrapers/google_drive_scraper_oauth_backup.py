#!/usr/bin/env python3
"""
Scraper pour Google Drive - Notes de Service
Utilise l'API Google Drive officielle
"""

import os
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleDriveScraper:
    """Scraper pour Google Drive avec authentification OAuth"""
    
    # ID des dossiers Google Drive (trouvés dans les iframes)
    FOLDER_2025_2026 = "1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB"
    FOLDER_ARCHIVES = "1ArnSC0QfJQmP2yeaej1mbPDJ30_zBCu-"
    
    # Scopes nécessaires (lecture seule)
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Google Drive scraper
        
        Args:
            credentials_path: Path to credentials.json
            token_path: Path to save/load token.pickle
        """
        if credentials_path is None:
            credentials_path = Path(__file__).parent / 'credentials.json'
        
        if token_path is None:
            token_path = Path(__file__).parent / 'token.pickle'
        
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            print("🔑 Chargement du token existant...")
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Rafraîchissement du token...")
                creds.refresh(Request())
            else:
                print("\n🔐 AUTHENTIFICATION REQUISE")
                print("="*80)
                print("Un navigateur va s'ouvrir pour vous connecter à Google.")
                print("Connectez-vous avec : tahar.guenfoud@eduhainaut.be")
                print("Autorisez l'accès en lecture à Google Drive.")
                print("="*80 + "\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Token sauvegardé !\n")
        
        # Build service
        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Connecté à Google Drive API\n")
    
    def list_files_in_folder(self, folder_id: str, days: int = 30) -> List[Dict]:
        """
        List files in a Google Drive folder
        
        Args:
            folder_id: Google Drive folder ID
            days: Filter files modified in last N days
            
        Returns:
            List of file metadata
        """
        if not self.service:
            self.authenticate()
        
        # Calculate date filter
        date_filter = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        
        print(f"📂 Recherche de fichiers dans le dossier {folder_id[:20]}...")
        
        try:
            # Query files
            query = f"'{folder_id}' in parents and trashed = false and modifiedTime > '{date_filter}'"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, createdTime, modifiedTime, webViewLink, size)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            print(f"✅ {len(files)} fichier(s) trouvé(s) (< {days} jours)\n")
            
            return files
        
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des fichiers: {e}")
            return []
    
    def get_recent_notes(self, days: int = 7) -> List[Dict]:
        """
        Get recent notes from both folders
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of notes with metadata
        """
        notes = []
        
        # Get files from 2025-2026 folder
        print("📋 Dossier NOTES DE SERVICE 2025-2026")
        print("="*80)
        files_2025 = self.list_files_in_folder(self.FOLDER_2025_2026, days=days)
        
        for file in files_2025:
            notes.append({
                'titre': file['name'],
                'contenu': f"Document: {file['name']} ({file.get('mimeType', 'Unknown type')})",
                'date_publication': file.get('modifiedTime', datetime.now().isoformat())[:10],
                'url': file.get('webViewLink', ''),
                'file_id': file['id'],
                'mime_type': file.get('mimeType'),
                'size': file.get('size', 0)
            })
            
            print(f"  📄 {file['name']}")
            print(f"     Date: {file.get('modifiedTime', 'N/A')[:10]}")
            print(f"     Type: {file.get('mimeType', 'N/A')}")
            print()
        
        print(f"\n📊 Total: {len(notes)} note(s) récente(s)\n")
        
        return notes


if __name__ == "__main__":
    print("🚀 Scraper Google Drive API\n")
    
    scraper = GoogleDriveScraper()
    
    # Get recent notes
    notes = scraper.get_recent_notes(days=30)
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DES NOTES")
    print("="*80)
    
    for i, note in enumerate(notes, 1):
        print(f"\n{i}. {note['titre']}")
        print(f"   Date: {note['date_publication']}")
        print(f"   URL: {note['url']}")
