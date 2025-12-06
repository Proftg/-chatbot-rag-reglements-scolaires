# Plan d'Implémentation : Assistant École & Automatisation

## Problème Identifié
Le site de l'école (https://sites.google.com/eduhainaut.be/apm/accueil) est protégé par une authentification Google (Workspace/Edu). Cela signifie qu'un simple robot ne peut pas y accéder sans vos identifiants.

## Solution Proposée

### 1. Gestion de l'Authentification (Le plus critique)
Pour contourner la protection Google de manière sécurisée sans que vous me donniez votre mot de passe :
*   Nous utiliserons un script **Python avec Playwright**.
*   **Première fois** : Le script lance un navigateur *visible*. Vous vous connectez manuellement. Le script sauvegarde ensuite vos "cookies" de session dans un fichier sécurisé sur votre ordinateur.
*   **Ensuite** : L'automatisation utilise ces cookies pour accéder au site sans se reconnecter.

### 2. Architecture du Chatbot RAG (Règlement)
Pour simplifier la lecture du règlement :
*   **Extraction** : Le script récupère le texte des pages "Règlement".
*   **Indexation** : Nous découpons ce texte et l'enregistrons dans une base de données vectorielle locale (ChromaDB).
*   **Chatbot** : Une interface simple (en Python/Streamlit ou terminal) où vous posez des questions ("Quelle est la procédure pour une absence ?") et l'IA répond basée *uniquement* sur les documents de l'école.

### 3. Automatisation des "Notes de Service" (Email)
Pour recevoir les nouveautés par email :
*   **Comparaison** : Le script télécharge la page des notes de services. Il la compare avec la version de la veille.
*   **Détection** : Si un nouveau texte apparaît (ou un nouveau lien PDF), il est extrait.
*   **Notification** : Le script envoie un email via votre propre compte Gmail (en utilisant un "Mot de passe d'application" Google, très simple à configurer).
*   **Planification** : Nous configurerons le script pour qu'il s'exécute automatiquement (via le Planificateur de tâches Windows) chaque matin à votre arrivée.

## Organisation des Fichiers
```
AMP/
├── implementation_plan.md
├── requirements.txt
└── school_assistant/
    ├── auth/
    │   └── login_setup.py      # Authentification initiale
    ├── scraper/
    │   ├── fetch_notes.py      # Récupération des nouveautés
    │   └── fetch_reglement.py  # Aspiration du règlement
    ├── chatbot/
    │   └── bot.py              # Interface de chat
    └── daily_check.py          # Script principal automatisé
```
