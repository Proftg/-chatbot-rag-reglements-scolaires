#!/bin/bash
###############################################################################
# Script d'installation automatique pour le projet School Assistant APM
# Usage: bash install.sh
###############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_header() {
    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}   $1${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python ${PYTHON_VERSION} trouvé"
        return 0
    else
        print_error "Python 3 non trouvé"
        return 1
    fi
}

check_git() {
    if command -v git &> /dev/null; then
        print_success "Git installé"
        return 0
    else
        print_warning "Git non trouvé (optionnel)"
        return 1
    fi
}

###############################################################################
# DÉBUT DE L'INSTALLATION
###############################################################################

print_header "INSTALLATION SCHOOL ASSISTANT APM"

# 1. Vérification des prérequis
print_info "Vérification des prérequis..."
check_python || { print_error "Python 3.10+ requis. Installez-le d'abord."; exit 1; }
check_git

# 2. Installation des dépendances Python
print_header "Installation des dépendances Python"

if [ ! -f "requirements.txt" ]; then
    print_error "Fichier requirements.txt non trouvé"
    exit 1
fi

print_info "Installation via pip..."
pip install -r requirements.txt --break-system-packages --quiet

print_success "Dépendances Python installées"

# 3. Configuration de l'environnement
print_header "Configuration de l'environnement"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Création du fichier .env depuis .env.example..."
        cp .env.example .env
        print_warning "⚠️  IMPORTANT : Éditez .env avec vos valeurs !"
        print_info "nano .env"
    else
        print_error ".env.example non trouvé"
    fi
else
    print_success "Fichier .env déjà existant"
fi

# 4. Création de la structure de dossiers
print_header "Création de la structure"

DIRS=("logs" "school_assistant/data" "school_assistant/auth/state")

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "Dossier créé : $dir"
    else
        print_info "Dossier existant : $dir"
    fi
done

# 5. Extraction des PDFs
print_header "Extraction des documents PDF"

if [ -d "Réglements" ]; then
    PDF_COUNT=$(find Réglements -name "*.pdf" -o -name "*.PDF" | wc -l)
    print_info "Trouvé ${PDF_COUNT} fichiers PDF"
    
    print_info "Extraction en cours..."
    python3 school_assistant/scraper/ingest_local_pdfs.py
    
    print_success "Extraction terminée"
else
    print_warning "Dossier Réglements/ non trouvé - Étape ignorée"
fi

# 6. Construction de l'index RAG
print_header "Construction de l'index RAG"

if [ -d "data" ] && [ "$(ls -A data/*.txt 2>/dev/null)" ]; then
    print_info "Construction de l'index FAISS..."
    python3 school_assistant/chatbot/setup_rag.py
    print_success "Index RAG construit"
else
    print_warning "Pas de fichiers .txt dans data/ - Index non construit"
fi

# 7. Installation OCR (optionnel)
print_header "Installation OCR (Optionnel)"

print_info "Tesseract OCR permet d'extraire les PDFs scannés"
read -p "Installer Tesseract OCR ? (o/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[OoYy]$ ]]; then
    print_info "Installation de Tesseract..."
    sudo apt update -qq
    sudo apt install -y tesseract-ocr tesseract-ocr-fra poppler-utils -qq
    pip install pytesseract pdf2image --break-system-packages --quiet
    print_success "Tesseract OCR installé"
    
    print_info "Extraction des PDFs scannés..."
    python3 school_assistant/scraper/extract_with_ocr.py
    
    # Reconstruire l'index
    print_info "Reconstruction de l'index avec les nouveaux documents..."
    python3 school_assistant/chatbot/setup_rag.py
else
    print_info "Installation OCR ignorée"
fi

# 8. Installation Ollama (optionnel)
print_header "Installation Ollama (LLM Local - Optionnel)"

print_info "Ollama permet d'utiliser un LLM gratuitement en local"
read -p "Installer Ollama + Mistral ? (o/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[OoYy]$ ]]; then
    if ! command -v ollama &> /dev/null; then
        print_info "Installation d'Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        print_success "Ollama installé"
    else
        print_success "Ollama déjà installé"
    fi
    
    print_info "Téléchargement du modèle Mistral (peut prendre quelques minutes)..."
    ollama pull mistral
    print_success "Modèle Mistral téléchargé"
else
    print_info "Installation Ollama ignorée"
fi

# 9. Validation finale
print_header "Validation de l'installation"

python3 school_assistant/utils/validators.py

# 10. Résumé et prochaines étapes
print_header "INSTALLATION TERMINÉE !"

echo ""
print_success "Installation réussie !"
echo ""
print_info "Prochaines étapes :"
echo ""
echo "1. Éditez votre configuration :"
echo "   nano .env"
echo ""
echo "2. Configurez l'authentification (pour le scraping) :"
echo "   python3 school_assistant/auth/login_setup.py"
echo ""
echo "3. Testez le chatbot :"
echo "   python3 school_assistant/chatbot/bot.py"
echo "   ou"
echo "   python3 school_assistant/chatbot/bot.py 'Votre question'"
echo ""
echo "4. Lancez l'interface web :"
echo "   streamlit run school_assistant/interface/app.py"
echo ""
echo "5. Automatisez les vérifications quotidiennes :"
echo "   crontab -e"
echo "   0 7 * * * cd $(pwd) && python3 school_assistant/daily_check.py >> logs/cron.log 2>&1"
echo ""

print_info "Documentation complète : README.md"

echo ""
print_header "Bon usage ! 🎓"
