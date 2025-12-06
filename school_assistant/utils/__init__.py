"""
Utilitaires pour l'application School Assistant
"""
from .logger import setup_logger, log_query_metrics, log_scraping_event, log_email_notification

__all__ = [
    'setup_logger',
    'log_query_metrics', 
    'log_scraping_event',
    'log_email_notification'
]
