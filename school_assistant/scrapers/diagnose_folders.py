#!/usr/bin/env python3
"""
Diagnostic approfondi des dossiers Google Drive
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = '/home/tahar/project/AMP/school_assistant/scrapers/service-account.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

FOLDER_2025_2026 = '1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB'

def main():
    print("🔍 DIAGNOSTIC APPROFONDI")
    print("=" * 80)
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    
    # Test 1: Lister TOUT ce qui est dans le dossier (y compris dossiers)
    print("\n📋 Test 1: Lister TOUT le contenu du dossier parent")
    try:
        results = service.files().list(
            q=f"'{FOLDER_2025_2026}' in parents and trashed=false",
            fields="files(id, name, mimeType, permissions)",
            pageSize=100
        ).execute()
        
        items = results.get('files', [])
        print(f"✅ {len(items)} élément(s) trouvé(s)\n")
        
        for item in items:
            item_type = "📁" if item['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
            print(f"{item_type} {item['name']}")
            print(f"   ID: {item['id']}")
            print(f"   Type: {item['mimeType']}")
            print()
    except HttpError as error:
        print(f"❌ Erreur: {error}")
    
    # Test 2: Essayer d'accéder directement aux IDs des sous-dossiers connus
    print("\n📋 Test 2: Tenter d'accéder aux sous-dossiers par recherche")
    try:
        # Chercher des dossiers dont le nom contient "2025"
        results = service.files().list(
            q=f"name contains '2025' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name, parents)",
            pageSize=20
        ).execute()
        
        folders = results.get('files', [])
        print(f"✅ {len(folders)} dossier(s) contenant '2025'\n")
        
        for folder in folders:
            print(f"📁 {folder['name']}")
            print(f"   ID: {folder['id']}")
            print(f"   Parents: {folder.get('parents', 'Aucun')}")
            print()
    except HttpError as error:
        print(f"❌ Erreur: {error}")
    
    # Test 3: Vérifier les permissions du dossier parent
    print("\n📋 Test 3: Vérifier les permissions du dossier parent")
    try:
        folder_info = service.files().get(
            fileId=FOLDER_2025_2026,
            fields="id, name, permissions, capabilities"
        ).execute()
        
        print(f"📁 {folder_info['name']}")
        print(f"   Capabilities: {folder_info.get('capabilities', {})}")
        print(f"   Permissions: {len(folder_info.get('permissions', []))} permission(s)")
    except HttpError as error:
        print(f"❌ Erreur: {error}")

if __name__ == '__main__':
    main()
