#!/usr/bin/env python3
"""Test de connexion Groq"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ Erreur : GROQ_API_KEY manquant dans .env")
        return False
    
    print("🧪 Test de connexion à Groq...")
    print(f"   Clé API : {api_key[:8]}...")
    
    try:
        from groq import Groq
        
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Réponds juste 'Bonjour' en français."}],
            max_tokens=50
        )
        
        print(f"\n✅ SUCCÈS ! Groq répond : {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        return False

if __name__ == "__main__":
    success = test_groq()
    exit(0 if success else 1)
