import shutil
import os
import sys

path = os.path.join("school_assistant", "data", "chroma_db")
if os.path.exists(path):
    try:
        shutil.rmtree(path)
        print("Ancienne base de données supprimée.")
    except Exception as e:
        print(f"Erreur suppression : {e}")
else:
    print("Pas de base de données trouvée.")
