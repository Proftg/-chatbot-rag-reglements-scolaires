#!/usr/bin/env python3
"""
🚀 Configuration Automatique - Chatbot École
Script interactif pour configurer DeepSeek et l'index RAG
"""

import os
import sys
from pathlib import Path

def print_header(title):
    """Affiche un en-tête stylisé."""
    print("\n" + "="*70)
    print(f"   {title}")
    print("="*70 + "\n")

def check_api_key():
    """Vérifie si la clé API est configurée."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key.startswith("sk-proj"):
        return False, None
    
    return True, api_key

def configure_api_key():
    """Guide l'utilisateur pour configurer la clé DeepSeek."""
    print("📝 Configuration de la Clé DeepSeek\n")
    print("1. Allez sur : https://platform.deepseek.com/api_keys")
    print("2. Créez un compte si nécessaire")
    print("3. Créez une nouvelle clé API")
    print("4. Copiez la clé (format: sk-xxxxxxxxxxxx)")
    print()
    
    api_key = input("Collez votre clé DeepSeek ici : ").strip()
    
    if not api_key.startswith("sk-"):
        print("❌ Erreur : La clé doit commencer par 'sk-'")
        return False
    
    # Mettre à jour le fichier .env
    env_file = Path("/home/tahar/project/AMP/.env")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remplacer la ligne OPENAI_API_KEY
    with open(env_file, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith("OPENAI_API_KEY="):
                f.write(f"OPENAI_API_KEY={api_key}\n")
            else:
                f.write(line)
    
    print(f"✅ Clé sauvegardée dans .env : {api_key[:12]}...")
    return True

def test_deepseek_connection(api_key):
    """Teste la connexion à DeepSeek."""
    print("\n🧪 Test de connexion à DeepSeek...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0,
            max_tokens=50
        )
        
        response = llm.invoke("Dis juste 'Bonjour' en français.")
        print(f"✅ SUCCÈS ! DeepSeek répond : {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

def switch_to_new_index():
    """Active le nouvel index RAG optimisé."""
    print("\n📊 Activation du nouvel index RAG...")
    
    old_index = Path("/home/tahar/project/AMP/school_assistant/data/faiss_index")
    new_index = Path("/home/tahar/project/AMP/school_assistant/data/faiss_index_new")
    backup_index = Path("/home/tahar/project/AMP/school_assistant/data/faiss_index_old")
    
    if not new_index.exists():
        print("⚠️  Le nouvel index n'existe pas. Reconstruction nécessaire...")
        return False
    
    # Backup de l'ancien index
    if old_index.exists():
        if backup_index.exists():
            import shutil
            shutil.rmtree(backup_index)
        old_index.rename(backup_index)
        print(f"   📦 Ancien index sauvegardé dans faiss_index_old")
    
    # Activer le nouveau
    new_index.rename(old_index)
    print(f"   ✅ Nouvel index activé (529 chunks)")
    
    return True

def test_chatbot():
    """Teste le chatbot avec une question."""
    print("\n🤖 Test du Chatbot...\n")
    
    question = "Comment justifier une absence?"
    print(f"Question : {question}")
    print("-" * 70)
    
    os.system(f'cd /home/tahar/project/AMP/school_assistant/chatbot && python3 bot.py "{question}"')
    
    return True

def show_next_steps():
    """Affiche les prochaines étapes."""
    print_header("✅ CONFIGURATION TERMINÉE !")
    
    print("""
🎯 Votre chatbot est maintenant prêt !

COMMANDES UTILES :

1. 💬 Poser une question au chatbot :
   cd school_assistant/chatbot
   python3 bot.py "Votre question ici"

2. 🌐 Lancer l'interface web :
   streamlit run school_assistant/interface/app.py
   → Ouvrez http://localhost:8501

3. 📧 Tester les notifications email :
   python3 school_assistant/daily_check.py

4. 🔄 Mettre à jour l'index RAG :
   python3 test_rag_rebuild.py

EXEMPLES DE QUESTIONS :
- "Quels sont les horaires de l'école ?"
- "Comment justifier une absence ?"
- "Quel est le règlement du laboratoire informatique ?"
- "Que dit le règlement sur les smartphones ?"

📚 GUIDE COMPLET : Voir GUIDE_DEEPSEEK.md
""")

def main():
    """Fonction principale."""
    print_header("🚀 CONFIGURATION AUTOMATIQUE - CHATBOT ÉCOLE")
    
    # Étape 1 : Vérifier la clé API
    has_key, api_key = check_api_key()
    
    if not has_key:
        print("⚠️  Aucune clé DeepSeek valide trouvée.\n")
        
        choice = input("Voulez-vous configurer DeepSeek maintenant ? (o/n) : ").lower()
        
        if choice != 'o':
            print("\n📖 Consultez le guide : cat GUIDE_DEEPSEEK.md")
            print("   Ou ouvrez : https://platform.deepseek.com/api_keys")
            return
        
        if not configure_api_key():
            return
        
        # Recharger
        has_key, api_key = check_api_key()
    else:
        print(f"✅ Clé DeepSeek détectée : {api_key[:12]}...")
    
    # Étape 2 : Tester la connexion
    if not test_deepseek_connection(api_key):
        print("\n❌ La connexion à DeepSeek a échoué.")
        print("   Vérifiez votre clé API sur : https://platform.deepseek.com/api_keys")
        return
    
    # Étape 3 : Activer le nouvel index
    if not switch_to_new_index():
        print("\n⚠️  Reconstruction de l'index recommandée.")
        choice = input("Voulez-vous reconstruire l'index maintenant ? (o/n) : ").lower()
        
        if choice == 'o':
            print("\n🔧 Reconstruction de l'index RAG...")
            os.system("python3 /home/tahar/project/AMP/test_rag_rebuild.py")
            switch_to_new_index()
    
    # Étape 4 : Test final du chatbot
    choice = input("\nVoulez-vous tester le chatbot maintenant ? (o/n) : ").lower()
    
    if choice == 'o':
        test_chatbot()
    
    # Étape 5 : Afficher les prochaines étapes
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuration interrompue par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)
