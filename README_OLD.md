# 🎓 Chatbot RAG - Règlements Scolaires APM

Assistant intelligent basé sur RAG (Retrieval-Augmented Generation) pour faciliter l'accès aux règlements de l'Académie Provinciale des Métiers.

## 🌟 Fonctionnalités

- 🤖 **Chatbot Intelligent** : Pose des questions en langage naturel sur les règlements
- 📧 **Notifications Automatiques** : Alerte email quotidienne sur les nouvelles notes de service
- 🔍 **Recherche Sémantique** : RAG avec 529 chunks issus de 12 documents PDF
- 🌐 **Interface Web** : Application Streamlit multi-onglets
- 🔐 **Authentification** : Connexion automatique via Playwright pour les sites protégés

## 🚀 Installation Rapide

### Prérequis
- Python 3.10+
- Ubuntu/WSL ou Linux
- Compte DeepSeek (gratuit)

### Installation

```bash
# 1. Cloner/Accéder au projet
cd /home/tahar/project/AMP

# 2. Installer les dépendances
pip install -r requirements.txt --break-system-packages

# 3. Installer Playwright
playwright install chromium

# 4. Configuration automatique
python3 setup_complete.py
```

Le script `setup_complete.py` vous guidera pour :
- ✅ Configurer votre clé DeepSeek
- ✅ Tester la connexion
- ✅ Activer l'index RAG optimisé
- ✅ Lancer votre premier test

## 📖 Documentation

### Guides Disponibles

- **`GUIDE_DEEPSEEK.md`** : Migration complète vers DeepSeek (recommandé)
- **`implementation_plan.md`** : Plan d'architecture original

### Structure du Projet

```
AMP/
├── requirements.txt              # Dépendances
├── .env                         # Configuration (SECRET - ne pas commit)
├── setup_complete.py            # 🚀 Script de configuration automatique
├── test_rag_rebuild.py          # Reconstruction de l'index RAG
├── test_deepseek.py             # Test de connexion DeepSeek
│
├── Réglements/                  # 📄 12 PDFs sources
│   ├── ROI secondaire 2025-2026.pdf
│   ├── RGE_2025-26...pdf
│   └── ...
│
├── data/                        # Textes extraits (.txt)
│
└── school_assistant/
    ├── auth/                    # Authentification Playwright
    │   └── login_setup.py
    │
    ├── scraper/                 # Extraction de données
    │   ├── ingest_local_pdfs.py
    │   ├── fetch_notes.py
    │   └── fetch_reglement.py
    │
    ├── chatbot/                 # 🤖 Moteur RAG
    │   ├── setup_rag.py        # Construction de l'index
    │   └── bot.py              # Interface chatbot
    │
    ├── interface/               # 🌐 Application web
    │   └── app.py              # Streamlit
    │
    ├── data/                    # Base de données
    │   └── faiss_index/        # Index vectoriel (529 chunks)
    │
    └── daily_check.py           # 📧 Automatisation quotidienne
```

## 💬 Utilisation

### 1. Mode Terminal (Rapide)

```bash
cd school_assistant/chatbot
python3 bot.py "Comment justifier une absence?"
```

**Exemples de questions** :
- "Quels sont les horaires de l'école ?"
- "Que dit le règlement sur les smartphones ?"
- "Comment justifier une absence ?"
- "Quel est le règlement du laboratoire informatique ?"

### 2. Interface Web (Convivial)

```bash
streamlit run school_assistant/interface/app.py
```

Ouvrez http://localhost:8501 dans votre navigateur.

**Onglets disponibles** :
- 🤖 **Chatbot** : Questions/réponses avec historique
- 📋 **Notes de Service** : Dernières notes extraites
- ⚙️ **Système** : État et maintenance

### 3. Vérification Quotidienne Automatique

```bash
# Test manuel
python3 school_assistant/daily_check.py

# Automatiser (cron)
crontab -e
# Ajouter : 0 8 * * * cd /home/tahar/project/AMP && python3 school_assistant/daily_check.py
```

Envoie un email à `taharguenfoud@gmail.com` si nouvelle note de service détectée.

## 🔧 Configuration

### Fichier `.env` (obligatoire)

```env
# Clé DeepSeek (compatible OpenAI API)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# Email (notifications)
SENDER_EMAIL=tahar.guenfoud@eduhainaut.be
GMAIL_APP_PASSWORD=xxxxxxxxxxxx
RECEIVER_EMAIL=taharguenfoud@gmail.com
```

### Obtenir une Clé DeepSeek

1. Allez sur https://platform.deepseek.com/api_keys
2. Créez un compte (gratuit)
3. Créez une clé API
4. Copiez dans `.env`

**Avantages DeepSeek vs OpenAI** :
- 💰 **70x moins cher** : $0.14/1M tokens vs $2/1M
- ⚡ **Plus rapide**
- 🇫🇷 **Excellent en français**
- 🆓 **Quota gratuit généreux**

## 📊 Statistiques du Système

### État Actuel
- **Documents** : 7/12 PDFs extraits (5 nécessitent OCR)
- **Chunks RAG** : 529 morceaux (~850 caractères/chunk)
- **Caractères** : 403 024 au total
- **Embeddings** : all-MiniLM-L6-v2 (384 dimensions)
- **Vector Store** : FAISS
- **LLM** : DeepSeek-Chat

### Performance
- **Temps de réponse** : ~2-5 secondes
- **Précision** : Bonne (dépend de la qualité des PDFs sources)
- **Coût** : ~$0.001 par requête (avec DeepSeek)

## 🐛 Dépannage

### Problème : "Clé API invalide"

```bash
# Vérifier la clé
cat .env | grep OPENAI_API_KEY

# Tester la connexion
python3 test_deepseek.py
```

### Problème : "Aucun résultat trouvé"

```bash
# Vérifier l'index
ls -lh school_assistant/data/faiss_index/

# Reconstruire si nécessaire
python3 test_rag_rebuild.py
```

### Problème : "FAISS manquant"

```bash
pip install faiss-cpu --break-system-packages
```

### Problème : PDFs vides (5 fichiers)

Ces PDFs sont scannés et nécessitent OCR :
- Règlement atelier.pdf
- Projet éducatif et pédagogique Province de Hainaut.pdf
- Dress code - Section Coiffeur.pdf
- Règlement éducation physique.pdf
- Règlement de Travail - juillet 2024.pdf

**Solution** : Installer Tesseract OCR (voir `GUIDE_DEEPSEEK.md`)

## 🔒 Sécurité

### ⚠️ IMPORTANT : Ne jamais commit `.env`

```bash
# Vérifier que .env est ignoré
cat .gitignore | grep .env

# Si absent, ajouter
echo ".env" >> .gitignore
```

### Supprimer `.env` de l'historique Git (si déjà commit)

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

## 🚀 Améliorations Futures

### Court Terme
- [ ] Implémenter OCR pour les 5 PDFs scannés
- [ ] Migrer vers embeddings français (CamemBERT)
- [ ] Ajouter filtres par type de document
- [ ] Tests unitaires (pytest)

### Moyen Terme
- [ ] Hybrid Retrieval (FAISS + BM25)
- [ ] Re-ranking des résultats
- [ ] Cache des requêtes fréquentes
- [ ] Dashboard Analytics

### Long Terme
- [ ] Fine-tuning d'un modèle sur les règlements
- [ ] Multi-agent (spécialistes par type de règlement)
- [ ] API REST
- [ ] Déploiement Docker

## 📝 Changelog

### v1.0.0 (2025-12-06)
- ✅ Migration vers DeepSeek
- ✅ Index RAG optimisé (529 chunks)
- ✅ Interface Streamlit fonctionnelle
- ✅ Automatisation email
- ✅ Guides complets (GUIDE_DEEPSEEK.md)

## 🤝 Contribution

Ce projet est personnel mais ouvert aux suggestions.

**Contact** : taharguenfoud@gmail.com

## 📄 Licence

Projet éducatif - Utilisation personnelle

---

**Créé par** : TAHAR GUENFOUD  
**Pour** : Académie Provinciale des Métiers (APM)  
**Date** : Décembre 2025  
**Stack** : Python, LangChain, DeepSeek, FAISS, Streamlit, Playwright
