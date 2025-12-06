#!/bin/bash
# Script de création et publication du dépôt GitHub
# Auteur : TAHAR GUENFOUD

set -e  # Arrêter en cas d'erreur

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║   🚀 Publication du Projet sur GitHub                                       ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -f "README_GITHUB.md" ]; then
    echo "❌ Erreur : Exécutez ce script depuis le dossier racine du projet"
    exit 1
fi

# Étape 1 : Vérification des secrets
echo "🔍 ÉTAPE 1/6 : Vérification de la sécurité..."
echo ""

if grep -r "sk-proj-" .env 2>/dev/null || grep -r "gsk_" .env 2>/dev/null; then
    echo "⚠️  ATTENTION : Clés API détectées dans .env"
    echo "   ✅ C'est OK si .env est dans .gitignore"
fi

if git check-ignore .env > /dev/null 2>&1; then
    echo "✅ .env est bien ignoré par Git"
else
    echo "❌ ERREUR : .env n'est PAS dans .gitignore !"
    echo "   Ajoutez-le avant de continuer."
    exit 1
fi

echo ""

# Étape 2 : Renommer README
echo "📝 ÉTAPE 2/6 : Préparation du README..."
echo ""

if [ -f "README.md" ]; then
    echo "   Sauvegarde de l'ancien README → README_OLD.md"
    mv README.md README_OLD.md
fi

echo "   Activation du README GitHub"
cp README_GITHUB.md README.md

echo "✅ README prêt pour GitHub"
echo ""

# Étape 3 : Initialisation Git
echo "🔧 ÉTAPE 3/6 : Initialisation Git..."
echo ""

if [ -d ".git" ]; then
    echo "⚠️  Dépôt Git existant détecté"
    read -p "   Voulez-vous réinitialiser ? (y/N) : " reset_git
    if [ "$reset_git" = "y" ] || [ "$reset_git" = "Y" ]; then
        rm -rf .git
        git init
        echo "✅ Git réinitialisé"
    else
        echo "   Utilisation du dépôt existant"
    fi
else
    git init
    echo "✅ Git initialisé"
fi

echo ""

# Étape 4 : Vérification des fichiers à commit
echo "📦 ÉTAPE 4/6 : Préparation des fichiers..."
echo ""

# Ajouter tous les fichiers
git add .

# Afficher les fichiers qui seront commités
echo "   Fichiers à publier :"
git status --short | head -20
total_files=$(git status --short | wc -l)
echo "   ... ($total_files fichiers au total)"
echo ""

# Vérifier qu'aucun secret n'est ajouté
if git diff --cached --name-only | grep -E "\.env$|auth\.json$" > /dev/null 2>&1; then
    echo "❌ ERREUR : Fichiers secrets détectés dans le commit !"
    git diff --cached --name-only | grep -E "\.env$|auth\.json$"
    echo ""
    echo "   Annulez avec : git reset"
    exit 1
fi

echo "✅ Aucun secret détecté"
echo ""

# Étape 5 : Premier commit
echo "💾 ÉTAPE 5/6 : Création du commit initial..."
echo ""

git commit -m "🎓 Initial commit: Chatbot RAG pour règlements scolaires

✨ Fonctionnalités :
- Système RAG avec FAISS + LangChain
- LLM Groq (Llama 3.3 70B)
- Interface Streamlit
- 529 chunks issus de 12 PDFs
- Notifications email automatiques
- 100% gratuit

🏗️ Stack : Python, LangChain, FAISS, Groq, Streamlit, Playwright

📊 Métriques :
- Temps de réponse : 2-3s
- Précision : 85-90%
- Coût : \$0/mois
"

echo "✅ Commit créé"
echo ""

# Étape 6 : Instructions GitHub
echo "🌐 ÉTAPE 6/6 : Publication sur GitHub"
echo "══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 MAINTENANT, SUIVEZ CES ÉTAPES :"
echo ""
echo "1️⃣  Créer le dépôt sur GitHub :"
echo "   - Allez sur : https://github.com/new"
echo "   - Nom du dépôt : chatbot-rag-reglements-scolaires"
echo "   - Description : 🎓 Assistant RAG intelligent pour règlements scolaires"
echo "   - Visibilité : Public (pour portfolio) ou Private"
echo "   - ❌ NE PAS initialiser avec README/LICENSE (déjà créés)"
echo "   - Cliquez 'Create repository'"
echo ""
echo "2️⃣  Ensuite, exécutez ces commandes ICI :"
echo ""
echo "   # Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub"
echo "   git remote add origin https://github.com/VOTRE_USERNAME/chatbot-rag-reglements-scolaires.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "💡 CONSEIL : Ajoutez aussi des topics sur GitHub pour plus de visibilité :"
echo "   - rag"
echo "   - langchain"
echo "   - llm"
echo "   - chatbot"
echo "   - education"
echo "   - groq"
echo "   - faiss"
echo "   - python"
echo ""
echo "══════════════════════════════════════════════════════════════════════════════"
echo ""
read -p "Appuyez sur ENTRÉE pour ouvrir GitHub dans votre navigateur..."

# Ouvrir GitHub
if command -v xdg-open &> /dev/null; then
    xdg-open "https://github.com/new" &
elif command -v cmd.exe &> /dev/null; then
    cmd.exe /c start "https://github.com/new" &
fi

echo ""
echo "✅ Préparation terminée !"
echo ""
echo "Votre projet est prêt à être publié sur GitHub ! 🎉"
echo ""
