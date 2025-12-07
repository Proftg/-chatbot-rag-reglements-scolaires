#!/usr/bin/env python3
"""
Test d'accès aux dossiers Google Drive
Vérifie si le service account peut accéder aux dossiers partagés
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
SERVICE_ACCOUNT_FILE = '/home/tahar/project/AMP/school_assistant/scrapers/service-account.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# IDs des dossiers
FOLDER_2025_2026 = '1q2lbu4ULreu-zrnljdSQiIsMYlkKLdnB'
FOLDER_ARCHIVES = '1ArnSC0QfJQmP2yeaej1mbPDJ30_zBCu-'

def test_folder_access(service, folder_id, folder_name):
    """Teste l'accès à un dossier spécifique"""
    print(f"\n{'='*60}")
    print(f"Test d'accès au dossier: {folder_name}")
    print(f"Folder ID: {folder_id}")
    print('='*60)
    
    try:
        # Essayer de lister les fichiers dans le dossier
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=10,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        
        print(f"✅ ACCÈS RÉUSSI!")
        print(f"📁 {len(files)} élément(s) trouvé(s)\n")
        
        if files:
            for file in files:
                file_type = "📁" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
                print(f"{file_type} {file['name']}")
                print(f"   ID: {file['id']}")
                print(f"   Type: {file['mimeType']}")
                print(f"   Modifié: {file['modifiedTime']}")
                print()
        
        return True
        
    except HttpError as error:
        print(f"❌ ERREUR D'ACCÈS: {error}")
        if error.resp.status == 404:
            print("   → Le dossier n'existe pas ou n'est pas partagé avec le service account")
        elif error.resp.status == 403:
            print("   → Permission refusée - le dossier n'est pas partagé avec le service account")
        return False

def main():
    print("\n" + "="*60)
    print("TEST D'ACCÈS GOOGLE DRIVE - SERVICE ACCOUNT")
    print("="*60)
    
    try:
        # Authentification
        print("\n🔐 Authentification...")
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Authentification réussie!")
        print(f"Service account: {credentials.service_account_email}")
        
        # Test des deux dossiers
        success_2025 = test_folder_access(service, FOLDER_2025_2026, "NS 25-26")
        success_archives = test_folder_access(service, FOLDER_ARCHIVES, "NS Archives")
        
        # Résumé
        print("\n" + "="*60)
        print("RÉSUMÉ DES TESTS")
        print("="*60)
        print(f"Dossier NS 25-26: {'✅ OK' if success_2025 else '❌ ÉCHEC'}")
        print(f"Dossier Archives: {'✅ OK' if success_archives else '❌ ÉCHEC'}")
        
        if success_2025 and success_archives:
            print("\n🎉 TOUS LES TESTS RÉUSSIS!")
            print("Le système est prêt pour l'automatisation.")
        else:
            print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            print("Vérifiez que les dossiers sont bien partagés avec:")
            print(f"   {credentials.service_account_email}")
            print("Avec le rôle: Lecteur")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
