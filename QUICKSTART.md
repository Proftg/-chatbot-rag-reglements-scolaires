# 🚀 GUIDE DE DÉMARRAGE RAPIDE

Mise en route en 5 minutes pour le chatbot RAG de l'APM.

## 📋 Prérequis

- Ubuntu/WSL avec Python 3.10+
- 2GB d'espace disque libre
- Connexion Internet

## ⚡ Installation Express

### Option 1 : Script Automatique (Recommandé)

```bash
cd /home/tahar/project/AMP
chmod +x install.sh
./install.sh
```

Suivez les instructions interactives.

### Option 2 : Installation Manuelle

```bash
# 1. Installer les dépendances
pip install -r requirements.txt --break-system-packages

# 2. Configurer
cp .env.example .env
nano .env  # Éditer avec vos valeurs

# 3. Extraire les PDFs
python3 school_assistant/scraper/ingest_local_pdfs.py

# 4. Construire l'index
python3 school_assistant/chatbot/setup_rag.py
```

## 🎯 Utilisation Immédiate

### Chatbot en Ligne de Commande

```bash
# Question unique
python3 school_assistant/chatbot/bot.py "Comment justifier une absence?"

# Mode interactif
python3 school_assistant/chatbot/bot.py
```

### Interface Web

```bash
streamlit run school_assistant/interface/app.py
```

Ouvrir : http://localhost:8501

## 🔧 Configuration Minimale

Éditez `.env` avec au minimum :

```bash
# Pour le chatbot (optionnel si Ollama installé)
OPENAI_API_KEY=sk-proj-...

# Pour les notifications (optionnel)
SENDER_EMAIL=votre.email@eduhainaut.be
GMAIL_APP_PASSWORD=votre_mot_de_passe_app
RECEIVER_EMAIL=votre.email@gmail.com
```

## 🆘 Problèmes Fréquents

### "ModuleNotFoundError: No module named 'faiss'"
```bash
pip install faiss-cpu --break-system-packages
```

### "externally-managed-environment"
```bash
# Ajouter --break-system-packages à toutes les commandes pip
pip install <package> --break-system-packages
```

### Quota OpenAI épuisé
```bash
# Installer Ollama (LLM local gratuit)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

### PDFs vides
```bash
# Installer OCR
sudo apt install tesseract-ocr tesseract-ocr-fra
pip install pytesseract pdf2image --break-system-packages
python3 school_assistant/scraper/extract_with_ocr.py
```

## ✅ Vérification

```bash
# Tester la configuration
python3 school_assistant/utils/validators.py

# Tester le système
pytest tests/ -v
```

## 📚 Documentation Complète

Pour plus de détails, consultez :
- **README.md** - Documentation complète
- **RAPPORT_EXECUTION.md** - Détails techniques

## 🎓 Premiers Pas

1. **Testez le chatbot**
   ```bash
   python3 school_assistant/chatbot/bot.py "Quels sont les horaires?"
   ```

2. **Explorez l'interface web**
   ```bash
   streamlit run school_assistant/interface/app.py
   ```

3. **Configurez les notifications** (optionnel)
   ```bash
   python3 school_assistant/auth/login_setup.py
   python3 school_assistant/daily_check.py
   ```

## 📞 Support

**Email** : taharguenfoud@gmail.com

---

**Bon usage ! 🎓**
