#!/usr/bin/env python3
"""
Base de données pour les notes de service
Stockage SQLite avec gestion des doublons
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import hashlib

class NotesDatabase:
    """Gestion de la base de données des notes de service"""
    
    def __init__(self, db_path: str = "notes_service.db"):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier SQLite
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Crée la table si elle n'existe pas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes_service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                contenu TEXT NOT NULL,
                date_publication TEXT NOT NULL,
                date_scraping TEXT NOT NULL,
                url TEXT,
                hash TEXT UNIQUE NOT NULL,
                notified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index pour recherche rapide
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_date_publication 
            ON notes_service(date_publication)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notified 
            ON notes_service(notified)
        """)
        
        conn.commit()
        conn.close()
    
    def add_note(self, titre: str, contenu: str, date_publication: str, 
                 url: Optional[str] = None) -> bool:
        """
        Ajoute une note de service (si elle n'existe pas déjà)
        
        Args:
            titre: Titre de la note
            contenu: Contenu complet
            date_publication: Date de publication (format: YYYY-MM-DD)
            url: URL optionnelle
            
        Returns:
            True si ajoutée, False si doublon
        """
        # Créer un hash unique basé sur titre + date
        hash_content = f"{titre}|{date_publication}"
        note_hash = hashlib.md5(hash_content.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO notes_service 
                (titre, contenu, date_publication, date_scraping, url, hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                titre,
                contenu,
                date_publication,
                datetime.now().isoformat(),
                url,
                note_hash
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Doublon détecté
            return False
        finally:
            conn.close()
    
    def get_recent_notes(self, days: int = 7) -> List[Dict]:
        """
        Récupère les notes des N derniers jours
        
        Args:
            days: Nombre de jours (défaut: 7)
            
        Returns:
            Liste de notes triées par date (plus récentes d'abord)
        """
        date_limite = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, titre, contenu, date_publication, url, date_scraping
            FROM notes_service
            WHERE date_publication >= ?
            ORDER BY date_publication DESC
        """, (date_limite,))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                "id": row[0],
                "titre": row[1],
                "contenu": row[2],
                "date_publication": row[3],
                "url": row[4],
                "date_scraping": row[5]
            })
        
        conn.close()
        return notes
    
    def get_unnotified_notes(self) -> List[Dict]:
        """Récupère les notes non encore notifiées par email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, titre, contenu, date_publication, url
            FROM notes_service
            WHERE notified = 0
            ORDER BY date_publication DESC
        """)
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                "id": row[0],
                "titre": row[1],
                "contenu": row[2],
                "date_publication": row[3],
                "url": row[4]
            })
        
        conn.close()
        return notes
    
    def mark_as_notified(self, note_id: int):
        """Marque une note comme notifiée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notes_service
            SET notified = 1
            WHERE id = ?
        """, (note_id,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques sur les notes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM notes_service")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM notes_service 
            WHERE date_publication >= date('now', '-7 days')
        """)
        last_week = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM notes_service 
            WHERE notified = 0
        """)
        unnotified = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "last_week": last_week,
            "unnotified": unnotified
        }


if __name__ == "__main__":
    # Test de la base de données
    db = NotesDatabase()
    
    # Ajouter une note de test
    db.add_note(
        titre="Test - Installation système",
        contenu="Test de fonctionnement de la base de données.",
        date_publication=datetime.now().strftime("%Y-%m-%d"),
        url="https://example.com"
    )
    
    # Récupérer les notes récentes
    notes = db.get_recent_notes(days=7)
    print(f"\n✅ {len(notes)} note(s) récente(s):")
    for note in notes:
        print(f"  - {note['titre']} ({note['date_publication']})")
    
    # Statistiques
    stats = db.get_stats()
    print(f"\n📊 Statistiques:")
    print(f"  Total: {stats['total']}")
    print(f"  Dernière semaine: {stats['last_week']}")
    print(f"  Non notifiées: {stats['unnotified']}")
