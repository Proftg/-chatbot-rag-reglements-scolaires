#!/usr/bin/env python3
"""
Script de vérification quotidienne des notes de service
Avec logging amélioré et gestion d'erreurs robuste
"""
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scraper.fetch_notes import fetch_content
    from utils.logger import setup_logger, log_scraping_event, log_email_notification
except ImportError as e:
    print(f"ERREUR D'IMPORT: {e}")
    print("Assurez-vous d'être dans le bon dossier et que les dépendances sont installées.")
    sys.exit(1)

load_dotenv()

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Logger
logger = setup_logger('daily_check')


def validate_config() -> bool:
    """Valide que toutes les variables d'environnement sont présentes."""
    required_vars = {
        'SENDER_EMAIL': SENDER_EMAIL,
        'GMAIL_APP_PASSWORD': SENDER_PASSWORD,
        'RECEIVER_EMAIL': RECEIVER_EMAIL
    }
    
    missing = [var for var, value in required_vars.items() if not value]
    
    if missing:
        logger.error(f"Variables d'environnement manquantes : {', '.join(missing)}")
        logger.error("Créez un fichier .env basé sur .env.example")
        return False
    
    return True


def send_email(subject: str, body: str) -> bool:
    """
    Envoie un email via Gmail.
    
    Args:
        subject: Sujet de l'email
        body: Contenu de l'email
    
    Returns:
        True si succès, False sinon
    """
    if not SENDER_PASSWORD:
        logger.error("Impossible d'envoyer l'email : GMAIL_APP_PASSWORD manquant")
        return False

    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        log_email_notification(logger, RECEIVER_EMAIL, subject, True)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Échec d'authentification Gmail : {e}")
        logger.error("Vérifiez SENDER_EMAIL et GMAIL_APP_PASSWORD dans .env")
        log_email_notification(logger, RECEIVER_EMAIL, subject, False, str(e))
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email : {e}")
        log_email_notification(logger, RECEIVER_EMAIL, subject, False, str(e))
        return False


def compare_content(current: str, previous: str) -> tuple[bool, float]:
    """
    Compare deux contenus et retourne si un changement significatif est détecté.
    
    Args:
        current: Contenu actuel
        previous: Contenu précédent
    
    Returns:
        (changement_detecté, similarité_en_pourcentage)
    """
    from difflib import SequenceMatcher
    
    if not previous:
        return True, 0.0  # Premier run
    
    similarity = SequenceMatcher(None, previous, current).ratio()
    
    # Changement significatif si < 95% de similarité
    significant_change = similarity < 0.95
    
    return significant_change, similarity * 100


def main():
    """Fonction principale de vérification."""
    logger.info("="*70)
    logger.info(f"DÉBUT DU SCAN QUOTIDIEN : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70)
    
    # 1. Validation de la configuration
    if not validate_config():
        logger.error("Configuration invalide. Arrêt du script.")
        return 1
    
    # 2. Récupérer les notes actuelles
    logger.info("Récupération des notes de service...")
    current_content = fetch_content()
    
    if not current_content:
        logger.error("Échec de la récupération des notes")
        log_scraping_event(
            logger,
            "https://sites.google.com/eduhainaut.be/apm/notes-de-service",
            False,
            0,
            "Contenu vide retourné"
        )
        return 1
    
    log_scraping_event(
        logger,
        "https://sites.google.com/eduhainaut.be/apm/notes-de-service",
        True,
        len(current_content)
    )
    logger.info(f"Contenu récupéré : {len(current_content)} caractères")

    # 3. Charger les notes précédentes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    previous_file = os.path.join(base_dir, "data", "notes_previous.txt")
    
    previous_content = ""
    if os.path.exists(previous_file):
        with open(previous_file, "r", encoding="utf-8") as f:
            previous_content = f.read()
        logger.info(f"Notes précédentes chargées : {len(previous_content)} caractères")
    else:
        logger.info("Aucune note précédente trouvée (premier run)")

    # 4. Comparer
    has_changed, similarity = compare_content(current_content, previous_content)
    
    logger.info(f"Similarité avec version précédente : {similarity:.1f}%")
    
    if has_changed:
        logger.info(">> CHANGEMENT SIGNIFICATIF DÉTECTÉ !")
        
        # Préparer l'email
        subject = f"🔔 École APM : Nouvelles Notes de Service ({datetime.now().strftime('%d/%m/%Y')})"
        
        body = f"""Bonjour,

Le système a détecté une modification significative sur la page 'Notes de Service' de l'école.

Similarité avec la version précédente : {similarity:.1f}%

📋 EXTRAIT DU CONTENU ACTUEL :
{'='*70}
{current_content[:2000]}
{'...' if len(current_content) > 2000 else ''}
{'='*70}

🔗 Lien direct : https://sites.google.com/eduhainaut.be/apm/notes-de-service

---
Assistant Automatique APM
Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
"""
        
        # Envoyer l'email
        if send_email(subject, body):
            logger.info("Email de notification envoyé avec succès")
        else:
            logger.error("Échec de l'envoi de l'email de notification")
        
        # Mise à jour du fichier de référence
        try:
            with open(previous_file, "w", encoding="utf-8") as f:
                f.write(current_content)
            logger.info("Fichier de référence mis à jour")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du fichier : {e}")
            
    else:
        logger.info(">> Aucun changement significatif détecté")
    
    logger.info("="*70)
    logger.info("FIN DU SCAN QUOTIDIEN")
    logger.info("="*70)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Script interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Erreur fatale : {e}", exc_info=True)
        sys.exit(1)
