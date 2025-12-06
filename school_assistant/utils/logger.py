#!/usr/bin/env python3
"""
Système de logging centralisé pour l'application
"""
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Configure un logger avec rotation de fichiers.
    
    Args:
        name: Nom du module (ex: 'chatbot', 'scraper', 'daily_check')
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter les doublons si déjà configuré
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Créer le dossier logs
    base_dir = Path(__file__).resolve().parents[2]
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Handler fichier avec rotation (10MB max, 5 fichiers de backup)
    log_file = log_dir / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Handler console
    console_handler = logging.StreamHandler()
    
    # Format détaillé
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_query_metrics(
    logger: logging.Logger,
    question: str,
    num_docs_retrieved: int,
    llm_used: str,
    response_time: float,
    success: bool
):
    """
    Enregistre les métriques d'une requête de chatbot.
    
    Args:
        logger: Logger à utiliser
        question: Question posée
        num_docs_retrieved: Nombre de documents trouvés
        llm_used: LLM utilisé ('openai', 'ollama', 'none')
        response_time: Temps de réponse en secondes
        success: Succès ou échec
    """
    status = "SUCCESS" if success else "FAILED"
    logger.info(
        f"[QUERY] {status} | LLM: {llm_used} | Docs: {num_docs_retrieved} | "
        f"Time: {response_time:.2f}s | Q: '{question[:100]}...'"
    )


def log_scraping_event(
    logger: logging.Logger,
    url: str,
    success: bool,
    content_length: int = 0,
    error: str = None
):
    """
    Enregistre un événement de scraping.
    
    Args:
        logger: Logger à utiliser
        url: URL scrapée
        success: Succès ou échec
        content_length: Longueur du contenu récupéré
        error: Message d'erreur si échec
    """
    if success:
        logger.info(f"[SCRAPE] SUCCESS | URL: {url} | Size: {content_length} bytes")
    else:
        logger.error(f"[SCRAPE] FAILED | URL: {url} | Error: {error}")


def log_email_notification(
    logger: logging.Logger,
    recipient: str,
    subject: str,
    success: bool,
    error: str = None
):
    """
    Enregistre l'envoi d'un email.
    
    Args:
        logger: Logger à utiliser
        recipient: Destinataire
        subject: Sujet de l'email
        success: Succès ou échec
        error: Message d'erreur si échec
    """
    if success:
        logger.info(f"[EMAIL] SUCCESS | To: {recipient} | Subject: {subject}")
    else:
        logger.error(f"[EMAIL] FAILED | To: {recipient} | Error: {error}")


# Export des fonctions principales
__all__ = [
    'setup_logger',
    'log_query_metrics',
    'log_scraping_event',
    'log_email_notification'
]
