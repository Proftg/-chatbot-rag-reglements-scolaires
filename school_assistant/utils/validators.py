#!/usr/bin/env python3
"""
Validation de la configuration et des variables d'environnement
"""
import os
from typing import List, Optional, Dict
from pathlib import Path


class ConfigValidator:
    """Valide la configuration de l'application au démarrage."""
    
    # Variables d'environnement requises
    REQUIRED_ENV_VARS = {
        'email': ['SENDER_EMAIL', 'GMAIL_APP_PASSWORD', 'RECEIVER_EMAIL'],
        'llm': ['OPENAI_API_KEY'],  # Optionnel si Ollama est utilisé
    }
    
    # Dossiers requis
    REQUIRED_DIRS = [
        'Réglements',
        'data',
        'school_assistant/data',
        'school_assistant/auth/state'
    ]
    
    @classmethod
    def validate_env_vars(cls, category: str = 'all') -> Dict[str, List[str]]:
        """
        Valide les variables d'environnement.
        
        Args:
            category: 'email', 'llm', ou 'all'
        
        Returns:
            Dict avec les catégories et variables manquantes
        """
        missing = {}
        
        if category == 'all':
            categories = cls.REQUIRED_ENV_VARS.keys()
        else:
            categories = [category]
        
        for cat in categories:
            if cat not in cls.REQUIRED_ENV_VARS:
                continue
            
            cat_missing = [
                var for var in cls.REQUIRED_ENV_VARS[cat]
                if not os.getenv(var)
            ]
            
            if cat_missing:
                missing[cat] = cat_missing
        
        return missing
    
    @classmethod
    def validate_directories(cls, base_dir: Optional[Path] = None) -> List[str]:
        """
        Valide que les dossiers requis existent.
        
        Args:
            base_dir: Dossier racine du projet
        
        Returns:
            Liste des dossiers manquants
        """
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2]
        
        missing = []
        
        for dir_path in cls.REQUIRED_DIRS:
            full_path = base_dir / dir_path
            if not full_path.exists():
                missing.append(str(dir_path))
        
        return missing
    
    @classmethod
    def validate_database(cls, base_dir: Optional[Path] = None) -> bool:
        """
        Vérifie que la base de données FAISS existe.
        
        Args:
            base_dir: Dossier racine du projet
        
        Returns:
            True si la base existe, False sinon
        """
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2]
        
        db_dir = base_dir / "school_assistant" / "data" / "faiss_index"
        index_file = db_dir / "index.faiss"
        
        return index_file.exists()
    
    @classmethod
    def validate_auth(cls, base_dir: Optional[Path] = None) -> bool:
        """
        Vérifie que les cookies d'authentification existent.
        
        Args:
            base_dir: Dossier racine du projet
        
        Returns:
            True si les cookies existent, False sinon
        """
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2]
        
        auth_file = base_dir / "school_assistant" / "auth" / "state" / "auth.json"
        return auth_file.exists()
    
    @classmethod
    def full_validation(cls, verbose: bool = True) -> bool:
        """
        Effectue une validation complète de la configuration.
        
        Args:
            verbose: Afficher les détails
        
        Returns:
            True si tout est OK, False si des problèmes sont détectés
        """
        all_ok = True
        
        if verbose:
            print("\n" + "="*70)
            print("   VALIDATION DE LA CONFIGURATION")
            print("="*70 + "\n")
        
        # 1. Variables d'environnement
        missing_env = cls.validate_env_vars()
        
        if missing_env:
            all_ok = False
            if verbose:
                print("⚠️  Variables d'environnement manquantes :")
                for category, vars in missing_env.items():
                    print(f"   • {category}: {', '.join(vars)}")
                print("   → Créez un fichier .env basé sur .env.example\n")
        else:
            if verbose:
                print("✅ Variables d'environnement : OK\n")
        
        # 2. Dossiers
        missing_dirs = cls.validate_directories()
        
        if missing_dirs:
            all_ok = False
            if verbose:
                print("⚠️  Dossiers manquants :")
                for dir in missing_dirs:
                    print(f"   • {dir}")
                print()
        else:
            if verbose:
                print("✅ Structure de dossiers : OK\n")
        
        # 3. Base de données RAG
        has_db = cls.validate_database()
        
        if not has_db:
            all_ok = False
            if verbose:
                print("⚠️  Base de données RAG manquante")
                print("   → Exécutez : python school_assistant/chatbot/setup_rag.py\n")
        else:
            if verbose:
                print("✅ Base de données RAG : OK\n")
        
        # 4. Authentification
        has_auth = cls.validate_auth()
        
        if not has_auth:
            if verbose:
                print("⚠️  Cookies d'authentification manquants")
                print("   → Exécutez : python school_assistant/auth/login_setup.py")
                print("   (Requis uniquement pour le scraping des notes)\n")
        else:
            if verbose:
                print("✅ Authentification : OK\n")
        
        if verbose:
            print("="*70)
            if all_ok:
                print("✅ Configuration complète et fonctionnelle !")
            else:
                print("⚠️  Certains éléments nécessitent votre attention")
            print("="*70 + "\n")
        
        return all_ok


if __name__ == "__main__":
    # Test de validation
    ConfigValidator.full_validation(verbose=True)
