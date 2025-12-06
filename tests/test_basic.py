#!/usr/bin/env python3
"""
Tests unitaires pour le système School Assistant
Exécution : pytest tests/test_basic.py -v
"""
import pytest
import os
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from school_assistant.utils.validators import ConfigValidator


class TestConfigValidator:
    """Tests pour le validateur de configuration."""
    
    def test_validate_env_vars_all(self):
        """Test de validation de toutes les variables d'environnement."""
        missing = ConfigValidator.validate_env_vars('all')
        assert isinstance(missing, dict)
    
    def test_validate_directories(self):
        """Test de validation des dossiers."""
        base_dir = Path(__file__).parent.parent
        missing = ConfigValidator.validate_directories(base_dir)
        assert isinstance(missing, list)
    
    def test_validate_database_exists(self):
        """Test de l'existence de la base de données."""
        base_dir = Path(__file__).parent.parent
        has_db = ConfigValidator.validate_database(base_dir)
        assert isinstance(has_db, bool)


class TestTextProcessing:
    """Tests pour le prétraitement de texte."""
    
    def test_preprocess_text_removes_metadata(self):
        """Test de suppression des métadonnées."""
        from school_assistant.chatbot.setup_rag import preprocess_text
        
        text = "Content here\nlikes\ncomments\nMore content"
        result = preprocess_text(text)
        
        assert "likes" not in result.lower()
        assert "comments" not in result.lower()
    
    def test_preprocess_text_normalizes_whitespace(self):
        """Test de normalisation des espaces."""
        from school_assistant.chatbot.setup_rag import preprocess_text
        
        text = "Too    many     spaces"
        result = preprocess_text(text)
        
        assert "  " not in result
    
    def test_classify_document_roi(self):
        """Test de classification ROI."""
        from school_assistant.chatbot.setup_rag import classify_document
        
        filename = "ROI secondaire 2025-2026.pdf"
        doc_type = classify_document(filename)
        
        assert doc_type == "ROI"
    
    def test_classify_document_rge(self):
        """Test de classification RGE."""
        from school_assistant.chatbot.setup_rag import classify_document
        
        filename = "RGE_2025-26.pdf"
        doc_type = classify_document(filename)
        
        assert doc_type == "RGE"


class TestLogger:
    """Tests pour le système de logging."""
    
    def test_setup_logger(self):
        """Test de création d'un logger."""
        from school_assistant.utils.logger import setup_logger
        
        logger = setup_logger('test')
        assert logger is not None
        assert logger.name == 'test'
    
    def test_logger_has_handlers(self):
        """Test que le logger a des handlers."""
        from school_assistant.utils.logger import setup_logger
        
        logger = setup_logger('test2')
        assert len(logger.handlers) >= 1


class TestDocumentLoading:
    """Tests pour le chargement de documents."""
    
    def test_data_directory_exists(self):
        """Test que le dossier data existe."""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data"
        
        assert data_dir.exists(), "Le dossier data/ doit exister"
    
    def test_reglements_directory_exists(self):
        """Test que le dossier Réglements existe."""
        base_dir = Path(__file__).parent.parent
        reg_dir = base_dir / "Réglements"
        
        assert reg_dir.exists(), "Le dossier Réglements/ doit exister"
    
    def test_txt_files_exist(self):
        """Test que des fichiers .txt existent dans data/."""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data"
        
        txt_files = list(data_dir.glob("*.txt"))
        # Filtrer les fichiers temporaires
        txt_files = [f for f in txt_files if not any(skip in f.name for skip in ['notes_', 'reglement_raw'])]
        
        assert len(txt_files) > 0, "Au moins un fichier .txt doit exister dans data/"


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "--tb=short"])
