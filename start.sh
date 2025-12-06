#!/bin/bash
# 🚀 Script de Démarrage Rapide - Chatbot École

echo "======================================================================"
echo "   🚀 DÉMARRAGE RAPIDE - CHATBOT ÉCOLE"
echo "======================================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de vérification
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 installé"
        return 0
    else
        echo -e "${RED}✗${NC} $1 manquant"
        return 1
    fi
}

# 1. Vérifications des prérequis
echo "📋 Vérification des prérequis..."
check_command python3
check_command pip

# 2. Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env manquant !${NC}"
    echo ""
    echo "Création depuis .env.example..."
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}Action requise :${NC}"
    echo "1. Obtenez votre clé DeepSeek : https://platform.deepseek.com/api_keys"
    echo "2. Modifiez le fichier .env avec vos vraies valeurs"
    echo ""
    echo "Voulez-vous ouvrir .env maintenant ? (o/n)"
    read -r response
    if [ "$response" = "o" ]; then
        nano .env
    fi
fi

# 3. Vérifier les dépendances Python
echo ""
echo "📦 Vérification des dépendances Python..."
if python3 -c "import langchain, faiss, streamlit" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Dépendances installées"
else
    echo -e "${YELLOW}⚠️  Certaines dépendances manquent${NC}"
    echo ""
    echo "Voulez-vous les installer maintenant ? (o/n)"
    read -r response
    if [ "$response" = "o" ]; then
        pip install -r requirements.txt --break-system-packages
    fi
fi

# 4. Vérifier l'index RAG
echo ""
echo "🔍 Vérification de l'index RAG..."
if [ -d "school_assistant/data/faiss_index" ] && [ -f "school_assistant/data/faiss_index/index.faiss" ]; then
    size=$(du -sh school_assistant/data/faiss_index/index.faiss | cut -f1)
    echo -e "${GREEN}✓${NC} Index RAG présent (taille: $size)"
else
    echo -e "${YELLOW}⚠️  Index RAG manquant ou incomplet${NC}"
    echo ""
    echo "Voulez-vous reconstruire l'index maintenant ? (o/n)"
    read -r response
    if [ "$response" = "o" ]; then
        python3 test_rag_rebuild.py
    fi
fi

# 5. Menu principal
echo ""
echo "======================================================================"
echo "   ✅ SYSTÈME PRÊT !"
echo "======================================================================"
echo ""
echo "Que voulez-vous faire ?"
echo ""
echo "1) 🧪 Tester la connexion DeepSeek"
echo "2) 💬 Poser une question au chatbot (terminal)"
echo "3) 🌐 Lancer l'interface web (Streamlit)"
echo "4) 📧 Tester les notifications email"
echo "5) 🔄 Reconstruire l'index RAG"
echo "6) ⚙️  Configuration complète guidée"
echo "7) 📖 Afficher la documentation"
echo "8) ❌ Quitter"
echo ""
read -p "Votre choix (1-8) : " choice

case $choice in
    1)
        echo ""
        echo "🧪 Test de connexion DeepSeek..."
        python3 test_deepseek.py
        ;;
    2)
        echo ""
        read -p "Votre question : " question
        cd school_assistant/chatbot
        python3 bot.py "$question"
        ;;
    3)
        echo ""
        echo "🌐 Lancement de l'interface web..."
        echo "   → http://localhost:8501"
        streamlit run school_assistant/interface/app.py
        ;;
    4)
        echo ""
        echo "📧 Test des notifications email..."
        python3 school_assistant/daily_check.py
        ;;
    5)
        echo ""
        echo "🔄 Reconstruction de l'index RAG..."
        python3 test_rag_rebuild.py
        ;;
    6)
        echo ""
        echo "⚙️  Configuration guidée..."
        python3 setup_complete.py
        ;;
    7)
        echo ""
        echo "📖 Documentation disponible :"
        echo ""
        echo "  README.md          - Vue d'ensemble du projet"
        echo "  GUIDE_DEEPSEEK.md  - Guide complet DeepSeek"
        echo ""
        read -p "Afficher README.md ? (o/n) : " show
        if [ "$show" = "o" ]; then
            less README.md
        fi
        ;;
    8)
        echo ""
        echo "À bientôt ! 👋"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}Choix invalide${NC}"
        ;;
esac

echo ""
echo "======================================================================"
echo "Pour relancer ce menu : ./start.sh"
echo "======================================================================"
