#!/usr/bin/env python3
"""
Trouve le profil Chrome Windows depuis WSL
"""
import os
import json

# Chemins possibles du profil Chrome sur Windows (accessible depuis WSL)
possible_paths = [
    "/mnt/c/Users/tahar/AppData/Local/Google/Chrome/User Data",
    "/mnt/c/Users/tahar/AppData/Local/Google/Chrome/User Data/Default",
]

print("🔍 Recherche du profil Chrome...")
print("=" * 80)

for path in possible_paths:
    if os.path.exists(path):
        print(f"✅ TROUVÉ: {path}")
        
        # Vérifier si c'est bien un profil Chrome valide
        prefs_file = os.path.join(path, "Preferences")
        if os.path.exists(prefs_file):
            print(f"   ✅ Fichier Preferences trouvé - Profil valide")
            print(f"\n📋 Utilisez ce chemin pour Playwright:")
            print(f"   {path}")
        else:
            print(f"   ⚠️  Pas de fichier Preferences")
    else:
        print(f"❌ Pas trouvé: {path}")

print("\n" + "=" * 80)
