#!/usr/bin/env python3
"""
Scraper pour notes de service sur Google Sites
Avec Firefox et session persistante
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time
import json
from pathlib import Path

class GoogleSitesScraper:
    """Scraper pour les notes de service APM"""
    
    URL = "https://sites.google.com/eduhainaut.be/apm/notes-de-service"
    COOKIES_FILE = Path(__file__).parent / "google_session_firefox.json"
    
    def __init__(self, headless: bool = False, debug: bool = False):
        """
        Initialize scraper
        
        Args:
            headless: Run browser in headless mode (False par défaut pour voir)
            debug: Save HTML for inspection
        """
        self.headless = headless
        self.debug = debug
    
    def scrape_notes(self) -> List[Dict]:
        """
        Scrape notes de service from Google Sites
        
        Returns:
            List of notes with title, content, date
        """
        notes = []
        
        with sync_playwright() as p:
            # Launch FIREFOX
            print("🦊 Lancement de Firefox...")
            browser = p.firefox.launch(
                headless=self.headless,
                firefox_user_prefs={
                    "browser.cache.disk.enable": False,
                    "browser.cache.memory.enable": False,
                }
            )
            
            # Créer contexte avec cookies si disponibles
            context_options = {
                "viewport": {"width": 1280, "height": 720},
                "locale": "fr-FR",
            }
            
            if self.COOKIES_FILE.exists():
                print("🍪 Chargement de la session sauvegardée...")
                with open(self.COOKIES_FILE) as f:
                    context_options['storage_state'] = f.read()
            
            context = browser.new_context(**context_options)
            page = context.new_page()
            
            try:
                print(f"📡 Accès à {self.URL}")
                page.goto(self.URL, timeout=30000)
                
                # Attendre un peu
                time.sleep(3)
                
                # Vérifier si on doit se connecter
                current_url = page.url
                page_content = page.content()
                
                if "accounts.google.com" in current_url or "Sign in" in page_content or "Connexion" in page_content:
                    print("\n" + "="*80)
                    print("🔐 CONNEXION MANUELLE REQUISE")
                    print("="*80)
                    print("\n📝 INSTRUCTIONS:")
                    print("  1. Le navigateur Firefox est maintenant visible")
                    print("  2. Connectez-vous avec: tahar.guenfoud@eduhainaut.be")
                    print("  3. Naviguez jusqu'à la page des notes de service")
                    print("  4. Vérifiez que les notes sont bien affichées")
                    print("  5. Revenez à ce terminal et appuyez sur ENTRÉE")
                    print("\n💡 La session sera sauvegardée pour les prochaines fois !")
                    print("="*80 + "\n")
                    
                    input("👉 Appuyez sur ENTRÉE quand vous voyez les notes dans Firefox...")
                    
                    # Sauvegarder les cookies
                    storage_state = context.storage_state()
                    with open(self.COOKIES_FILE, 'w') as f:
                        json.dump(storage_state, f, indent=2)
                    print("✅ Session Firefox sauvegardée !")
                    print("   → Les prochaines exécutions seront automatiques !\n")
                else:
                    print("✅ Déjà connecté !")
                
                # Attendre le chargement complet
                print("⏳ Chargement de la page...")
                page.wait_for_load_state('networkidle', timeout=15000)
                time.sleep(3)
                
                # Récupérer le HTML
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # DEBUG: Sauvegarder HTML
                if self.debug:
                    debug_file = 'debug_page_firefox.html'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"📄 HTML sauvegardé dans {debug_file}")
                
                # Analyse de la structure
                print("\n🔍 ANALYSE DE LA STRUCTURE HTML:")
                print("="*80)
                
                # Compter les éléments
                all_divs = soup.find_all('div')
                all_articles = soup.find_all('article')
                all_sections = soup.find_all('section')
                
                print(f"📦 Éléments structurels:")
                print(f"   <div>: {len(all_divs)}")
                print(f"   <article>: {len(all_articles)}")
                print(f"   <section>: {len(all_sections)}")
                
                headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                print(f"\n📌 Titres trouvés: {len(headers)}")
                if headers:
                    for i, h in enumerate(headers[:15], 1):
                        text = h.get_text(strip=True)
                        if text:
                            print(f"  {i}. <{h.name}> {text[:70]}")
                
                paragraphs = soup.find_all('p')
                print(f"\n📝 Paragraphes: {len(paragraphs)}")
                if paragraphs:
                    for i, p in enumerate(paragraphs[:10], 1):
                        text = p.get_text(strip=True)
                        if len(text) > 20:
                            print(f"  {i}. {text[:100]}...")
                
                # Chercher des listes
                lists = soup.find_all(['ul', 'ol'])
                print(f"\n📋 Listes: {len(lists)}")
                
                # Extraction
                print("\n🧪 TENTATIVE D'EXTRACTION...")
                notes = self._extract_notes_smart(soup)
                
                if not notes:
                    print("\n⚠️ Aucune note extraite. Essayons une approche plus large...")
                    notes = self._extract_notes_alternative(soup)
                
                print(f"\n✅ {len(notes)} note(s) extraite(s)")
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Attendre avant de fermer pour voir le résultat
                if not self.headless:
                    print("\n⏸️  Le navigateur va rester ouvert 5 secondes...")
                    time.sleep(5)
                browser.close()
        
        return notes
    
    def _extract_notes_smart(self, soup) -> List[Dict]:
        """Extraction intelligente basée sur titres"""
        notes = []
        headers = soup.find_all(['h2', 'h3', 'h4'])
        
        print(f"   Analyse de {len(headers)} titres potentiels...")
        
        for header in headers:
            titre = header.get_text(strip=True)
            
            # Filtrer les titres non pertinents
            skip_keywords = ['accueil', 'menu', 'navigation', 'sign in', 'connexion']
            if len(titre) < 5 or any(kw in titre.lower() for kw in skip_keywords):
                continue
            
            # Extraire le contenu suivant
            contenu = ""
            next_elem = header.find_next_sibling()
            
            while next_elem and next_elem.name not in ['h1', 'h2', 'h3', 'h4']:
                if next_elem.name in ['p', 'div', 'span', 'ul', 'ol']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 10:
                        contenu += text + "\n\n"
                next_elem = next_elem.find_next_sibling()
            
            if len(contenu.strip()) > 20:
                date_str = self._extract_date_from_text(titre + " " + contenu)
                if not date_str:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                
                notes.append({
                    "titre": titre,
                    "contenu": contenu.strip(),
                    "date_publication": date_str,
                    "url": self.URL
                })
                print(f"  ✓ {titre[:60]}")
        
        return notes
    
    def _extract_notes_alternative(self, soup) -> List[Dict]:
        """Approche alternative : tout paragraphe avec contenu substantiel"""
        notes = []
        
        # Chercher tous les blocs de texte significatifs
        all_text_elements = soup.find_all(['div', 'p', 'article', 'section'])
        
        for elem in all_text_elements:
            text = elem.get_text(strip=True)
            
            # Si le texte est substantiel (>100 caractères)
            if len(text) > 100:
                # Chercher un titre potentiel dans les enfants
                titre_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                titre = titre_elem.get_text(strip=True) if titre_elem else text[:50]
                
                # Éviter les doublons
                if any(note['titre'] == titre for note in notes):
                    continue
                
                notes.append({
                    "titre": titre,
                    "contenu": text,
                    "date_publication": datetime.now().strftime("%Y-%m-%d"),
                    "url": self.URL
                })
                print(f"  ✓ Bloc trouvé: {titre[:60]}")
        
        return notes
    
    def _extract_date_from_text(self, text: str) -> str | None:
        """Extract date from text"""
        patterns = [
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy'),
            (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', 'ymd'),
        ]
        
        for pattern, format_type in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    groups = match.groups()
                    if format_type == 'ymd':
                        return f"{groups[0]}-{groups[1]:0>2}-{groups[2]:0>2}"
                    else:
                        return f"{groups[2]}-{groups[1]:0>2}-{groups[0]:0>2}"
                except:
                    pass
        
        return None
    
    def get_recent_notes(self, days: int = 7) -> List[Dict]:
        """Get recent notes"""
        all_notes = self.scrape_notes()
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        recent_notes = [n for n in all_notes if n['date_publication'] >= cutoff_date]
        print(f"\n📅 Notes récentes (<{days} jours): {len(recent_notes)}/{len(all_notes)}")
        
        return recent_notes


if __name__ == "__main__":
    print("🚀 Scraper avec Firefox\n")
    scraper = GoogleSitesScraper(headless=False, debug=True)
    notes = scraper.get_recent_notes(days=30)
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DES NOTES EXTRAITES")
    print("="*80)
    for i, note in enumerate(notes, 1):
        print(f"\n📌 Note {i}:")
        print(f"  Titre: {note['titre']}")
        print(f"  Date: {note['date_publication']}")
        print(f"  Contenu ({len(note['contenu'])} caractères):")
        print(f"  {note['contenu'][:200]}...")
