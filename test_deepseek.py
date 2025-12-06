#!/usr/bin/env python3
"""
Script de test pour vérifier que DeepSeek fonctionne
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def test_deepseek():
    """Test simple de DeepSeek."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Erreur : OPENAI_API_KEY manquant dans .env")
        return False
    
    print("🧪 Test de connexion à DeepSeek...")
    print(f"   Clé API : {api_key[:8]}...")
    
    try:
        llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0
        )
        
        response = llm.invoke("Réponds juste 'Bonjour' en français.")
        print(f"\n✅ SUCCÈS ! Réponse de DeepSeek :")
        print(f"   {response.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        return False

if __name__ == "__main__":
    success = test_deepseek()
    exit(0 if success else 1)
