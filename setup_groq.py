#!/usr/bin/env python3
"""
Configuration automatique pour Groq (alternative gratuite à DeepSeek)
"""
import os
import sys

def configure_groq():
    """Configure le système pour utiliser Groq."""
    
    print("="*70)
    print("   🚀 CONFIGURATION GROQ (Alternative Gratuite)")
    print("="*70)
    print()
    print("📝 ÉTAPES :")
    print()
    print("1. Ouvrez : https://console.groq.com/keys")
    print("2. Créez un compte (gratuit)")
    print("3. Cliquez 'Create API Key'")
    print("4. Copiez la clé (format: gsk_...)")
    print()
    print("="*70)
    print()
    
    # Ouvrir le navigateur
    import webbrowser
    print("🌐 Ouverture de la page Groq...")
    webbrowser.open("https://console.groq.com/keys")
    print()
    
    api_key = input("Collez votre clé Groq (gsk_...) : ").strip()
    
    if not api_key.startswith("gsk_"):
        print("❌ Erreur : La clé Groq doit commencer par 'gsk_'")
        return False
    
    print()
    print("✅ Clé Groq valide détectée !")
    print()
    
    # Installer groq
    print("📦 Installation de la bibliothèque Groq...")
    os.system("pip install groq --break-system-packages -q")
    
    # Mettre à jour le .env
    env_file = "/home/tahar/project/AMP/.env"
    print("📝 Mise à jour du fichier .env...")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Ajouter GROQ_API_KEY
    found_groq = False
    with open(env_file, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith("GROQ_API_KEY="):
                f.write(f"GROQ_API_KEY={api_key}\n")
                found_groq = True
            else:
                f.write(line)
        
        if not found_groq:
            f.write(f"\n# Clé API Groq (alternative gratuite)\n")
            f.write(f"GROQ_API_KEY={api_key}\n")
    
    print("✅ Configuration .env mise à jour !")
    print()
    
    # Modifier bot.py pour utiliser Groq
    print("🔧 Modification de bot.py pour utiliser Groq...")
    
    bot_file = "/home/tahar/project/AMP/school_assistant/chatbot/bot.py"
    
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    import shutil
    from datetime import datetime
    backup_file = f"{bot_file}.backup_groq_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(bot_file, backup_file)
    
    # Remplacer par Groq
    new_content = content.replace(
        'from langchain_openai import ChatOpenAI',
        '''from langchain_openai import ChatOpenAI
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False'''
    )
    
    new_content = new_content.replace(
        '''llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0
        )''',
        '''# Essayer Groq en priorité
            groq_key = os.getenv("GROQ_API_KEY")
            if GROQ_AVAILABLE and groq_key:
                llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    groq_api_key=groq_key,
                    temperature=0
                )
            else:
                # Fallback DeepSeek
                llm = ChatOpenAI(
                    model="deepseek-chat",
                    openai_api_key=api_key,
                    openai_api_base="https://api.deepseek.com/v1",
                    temperature=0
                )'''
    )
    
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ bot.py modifié ! (backup: {backup_file})")
    print()
    
    # Test
    print("🧪 Test de connexion Groq...")
    print()
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Dis juste 'Bonjour'"}],
            max_tokens=10
        )
        print(f"✅ SUCCÈS ! Groq répond : {response.choices[0].message.content}")
        print()
        return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

if __name__ == "__main__":
    success = configure_groq()
    
    if success:
        print("="*70)
        print("   ✅ GROQ CONFIGURÉ AVEC SUCCÈS !")
        print("="*70)
        print()
        print("Vous pouvez maintenant tester :")
        print()
        print("  cd school_assistant/chatbot")
        print('  python3 bot.py "Comment justifier une absence?"')
        print()
    else:
        print()
        print("Configuration échouée. Réessayez ou utilisez DeepSeek avec crédits.")
