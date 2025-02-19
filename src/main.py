import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import time
import json
import html
import re

from config.credentials import CredentialsManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class PortalScraper:
    def __init__(self):
        self.credentials_manager = CredentialsManager()
        self.credentials = self.credentials_manager.get_credentials()
        self.login_url = "https://laruche.polymtl.ca/sp/ssp/r/etudiant/recherche-mandats?p40_type_recherche=C&session=4571910543658"
        self.driver = None
        self.wait_time = 10
        self.mandats_file = "mandats.json"
        self.processed_mandats = self.load_processed_mandats()

    def setup_driver(self):
        """Initialise le navigateur"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Décommenter pour exécuter sans interface graphique
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def login(self):
        """Gère la connexion au portail"""
        try:
            # Accéder à la page de login
            self.driver.get(self.login_url)
            
            # Attendre que les éléments soient présents
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Trouver et remplir le champ username
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.credentials['username'])

            # Trouver et remplir le champ password
            password_field = wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.clear()
            password_field.send_keys(self.credentials['password'])

            # Trouver et cliquer sur le bouton de connexion
            login_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='submit']"))
            )
            login_button.click()

            # Vérifier si la connexion a réussi (attendre la redirection ou un élément de la page suivante)
            try:
                # Attendre que l'URL change ou qu'un élément de la page suivante apparaisse
                wait.until(lambda driver: driver.current_url != self.login_url)
                print("Connexion réussie!")
                return True
            except TimeoutException:
                # Vérifier s'il y a des messages d'erreur
                error_messages = self.driver.find_elements(By.CLASS_NAME, "errors")
                if error_messages:
                    print(f"Erreur de connexion: {error_messages[0].text}")
                else:
                    print("La connexion a échoué")
                return False

        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False

    def close(self):
        """Ferme le navigateur"""
        if self.driver:
            self.driver.quit()

    def load_processed_mandats(self):
        """Charge la liste des mandats déjà traités"""
        try:
            with open(self.mandats_file, 'r') as f:
                data = json.load(f)
                processed = set()
                
                # Parcourir chaque mandat de façon sécurisée
                for mandat in data:
                    if isinstance(mandat, dict):
                        # Essayer différentes clés possibles pour le code
                        code = mandat.get('code_mandat') or mandat.get('code') or mandat.get('id')
                        if code:
                            processed.add(str(code))
                
                print(f"Chargement de {len(processed)} mandats déjà traités")
                return processed
                
        except FileNotFoundError:
            print("Aucun fichier de mandats existant trouvé. Création d'un nouveau fichier.")
            return set()
        except json.JSONDecodeError:
            print("Erreur de lecture du fichier JSON. Création d'un nouveau fichier.")
            return set()
        except Exception as e:
            print(f"Erreur lors du chargement des mandats: {str(e)}")
            return set()

    def save_mandat(self, mandat_data):
        """Sauvegarde un mandat dans le fichier JSON"""
        try:
            try:
                with open(self.mandats_file, 'r') as f:
                    mandats = json.load(f)
            except FileNotFoundError:
                mandats = []
            
            mandats.append(mandat_data)
            
            with open(self.mandats_file, 'w', encoding='utf-8') as f:
                json.dump(mandats, f, ensure_ascii=False, indent=2)
            
            self.processed_mandats.add(mandat_data['code_mandat'])
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du mandat: {e}")

    def extract_mandat_details(self):
        """Extrait les détails spécifiques d'un mandat"""
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            details = {}
            
            # Fonction helper pour extraire le texte après un label
            def extract_after_label(label):
                try:
                    # Trouver l'élément contenant le label
                    xpath = f"//*[contains(text(), '{label}:')]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        # Obtenir le texte brut via JavaScript
                        sibling_element = element.find_element(By.XPATH, "following-sibling::*")
                        raw_text = self.driver.execute_script(
                            "return arguments[0].textContent;", 
                            sibling_element
                        )
                        
                        if raw_text:
                            # Nettoyer le texte
                            clean = raw_text.strip()
                            # Supprimer tous les caractères non-imprimables sauf les sauts de ligne
                            clean = ''.join(char for char in clean if char.isprintable() or char == '\n')
                            return clean
                except Exception as e:
                    print(f"Erreur lors de l'extraction pour {label}: {str(e)}")
                    return ''
                return ''

            # Mapping des champs
            fields = {
                'etat_mandat': 'État du mandat',
                'date_limite': 'Date limite pour postuler',
                'employeur': 'Employeur',
                'description_employeur': 'Description de l\'employeur',
                'site_web': 'Site Web',
                'lieu_travail': 'Lieu du travail',
                'mode_travail': 'Mode de travail',
                'precisions_mode_travail': 'Précisions sur le mode de travail',
                'code_mandat': 'Code du mandat',
                'debut_mandat': 'Début du mandat',
                'duree': 'Durée',
                'possibilite_prolongation': 'Possibilité de prolongation',
                'titre_mandat': 'Titre du mandat',
                'description_mandat': 'Description du mandat',
                'exigences_mandat': 'Exigences du mandat',
                'niveau_etudes': 'Niveau d\'études requis',
                'specialites': 'Spécialités'
            }

            # Extraire chaque champ
            for field, label in fields.items():
                details[field] = extract_after_label(label)

            # Ajouter l'URL
            details['url'] = self.driver.current_url

            # Vérifier si les données sont cohérentes
            for field, value in details.items():
                if 'ÃƒÆ' in value or 'Ã¢â‚¬' in value:
                    print(f"Attention: Possible problème d'encodage dans {field}")
                    # Tentative de nettoyage supplémentaire
                    try:
                        # Essayer de décoder/encoder plusieurs fois si nécessaire
                        cleaned = value.encode('latin1').decode('utf-8')
                        details[field] = cleaned
                    except:
                        pass

            return details

        except Exception as e:
            print(f"Erreur lors de l'extraction des détails: {str(e)}")
            return {}
        
    def extract_mandats(self):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # S'assurer que nous sommes sur la bonne page
            if not self.driver.current_url.startswith(self.login_url):
                print("Retour à la page principale...")
                self.driver.get(self.login_url)
                time.sleep(3)
            
            # Attendre que le tableau soit chargé
            table_xpath = "//table[contains(@class, 'mandats')]"
            wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
            
            # Stocker tous les liens et leurs URLs avant de commencer la navigation
            links = []
            elements = self.driver.find_elements(By.XPATH, f"{table_xpath}//a[contains(@href, 'mandat')]")
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    text = element.text
                    if href and text:
                        links.append({'url': href, 'text': text})
                except:
                    continue
            
            print(f"Nombre de mandats trouvés : {len(links)}")
            
            # URL de la page principale
            main_page_url = self.driver.current_url
            
            # Parcourir les liens stockés
            for index, link_data in enumerate(links, 1):
                try:
                    print(f"\nTraitement du mandat {index}/{len(links)}: {link_data['text']}")
                    
                    # Extraire le code du mandat de l'URL
                    code_mandat = link_data['url'].split("mandat=")[-1].split("&")[0]
                    
                    if code_mandat in self.processed_mandats:
                        print(f"Mandat {code_mandat} déjà traité, passage au suivant...")
                        continue
                    
                    # Naviguer vers la page du mandat
                    print(f"Navigation vers {link_data['url']}")
                    self.driver.execute_script(f"window.location.href = '{link_data['url']}';")
                    time.sleep(3)
                    
                    # Vérifier que la navigation a réussi
                    if "mandat=" in self.driver.current_url:
                        # Extraire les détails
                        details = self.extract_mandat_details()
                        
                        if details:
                            self.save_mandat(details)
                            print(f"Mandat {code_mandat} sauvegardé avec succès")
                        
                        # Retourner à la page principale
                        print("Retour à la page principale...")
                        self.driver.execute_script(f"window.location.href = '{main_page_url}';")
                        time.sleep(3)
                        
                        # Attendre que le tableau soit rechargé
                        wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
                    else:
                        print("Échec de la navigation vers le mandat")
                        self.driver.get(main_page_url)
                        time.sleep(3)
                    
                except Exception as e:
                    print(f"Erreur lors du traitement du mandat {index}: {str(e)}")
                    # Tenter de revenir à la page principale
                    try:
                        self.driver.get(main_page_url)
                        time.sleep(3)
                    except:
                        print("Erreur lors du retour à la page principale")
                    continue
            
            return True
            
        except Exception as e:
            print(f"Erreur générale: {str(e)}")
            return False

    def clean_dict(self, data):
        """Nettoie récursivement un dictionnaire"""
        if isinstance(data, dict):
            return {key: self.clean_dict(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.clean_dict(item) for item in data]
        elif isinstance(data, str):
            return self.clean_text(data)
        return data

    def save_mandat(self, mandat_data):
        """Sauvegarde un mandat dans le fichier JSON"""
        try:
            try:
                with open(self.mandats_file, 'r', encoding='utf-8') as f:
                    mandats = json.load(f)
            except FileNotFoundError:
                mandats = []
            except json.JSONDecodeError:
                print("Erreur de décodage JSON, création d'un nouveau fichier")
                mandats = []
            
            # Nettoyer les données avant la sauvegarde
            cleaned_data = self.clean_dict(mandat_data)
            
            mandats.append(cleaned_data)
            
            with open(self.mandats_file, 'w', encoding='utf-8') as f:
                json.dump(mandats, f, ensure_ascii=False, indent=2)
            
            self.processed_mandats.add(cleaned_data.get('code_mandat', ''))
            
            print(f"Mandat sauvegardé avec succès")
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du mandat: {str(e)}")
    def clean_existing_json(self):
        """Nettoie le fichier JSON existant"""
        try:
            with open(self.mandats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Nettoyer les données
            cleaned_data = self.clean_dict(data)
            
            # Sauvegarder les données nettoyées
            with open(self.mandats_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
                
            print("Nettoyage du fichier JSON terminé")
            
        except Exception as e:
            print(f"Erreur lors du nettoyage du fichier JSON: {str(e)}")

def main():
    scraper = PortalScraper()
    try:
        scraper.setup_driver()
        if scraper.login():
            print("Connexion réussie! Début de l'extraction des mandats...")
            scraper.extract_mandats()
            print("Extraction terminée. Appuyez sur 'q' et Enter pour quitter.")
            while input().lower() != 'q':
                pass
        else:
            print("Échec de la connexion")
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()