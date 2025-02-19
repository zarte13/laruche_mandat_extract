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
        self.wait_time = 2
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
            time.sleep(2)  # Attendre le chargement initial
            
            # Définir les XPath
            username_xpath = "/html/body/div[3]/main/div/div[2]/section/div/div[2]/form/h3/section[1]/div/label/input"
            password_xpath = "/html/body/div[3]/main/div/div[2]/section/div/div[2]/form/h3/section[2]/div/div[1]/label/input"
            login_button_xpath = "/html/body/div[3]/main/div/div[2]/section/div/div[2]/form/h3/div[1]/button"
            
            # Attendre que les éléments soient présents
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Trouver et remplir le champ username
            username_field = wait.until(
                EC.presence_of_element_located((By.XPATH, username_xpath))
            )
            username_field.clear()
            time.sleep(0.5)
            username_field.send_keys(self.credentials['username'])

            
            # Trouver et remplir le champ password
            password_field = wait.until(
                EC.presence_of_element_located((By.XPATH, password_xpath))
            )
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(self.credentials['password'])

            
            # Trouver et cliquer sur le bouton de connexion
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, login_button_xpath))
            )
            time.sleep(0.5)
            login_button.click()
            
            # Vérifier si la connexion a réussi
            try:
                # Attendre que l'URL change
                wait.until(lambda driver: driver.current_url != self.login_url)
                print("Connexion réussie!")
                return True
            except TimeoutException:
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

    def extract_mandats(self):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # S'assurer que nous sommes sur la bonne page
            if not self.driver.current_url.startswith(self.login_url):
                print("Retour à la page principale...")
                self.driver.get(self.login_url)
                time.sleep(0.5)
            
            # Attendre que le tableau soit chargé
            table_rows = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//tr[.//a[contains(@href, 'mandat')]]")
            ))
            
            main_window = self.driver.current_window_handle
            
            links = []
            for row in table_rows:
                try:
                    link_element = row.find_element(By.XPATH, ".//a[contains(@href, 'mandat')]")
                    code_mandat = row.find_element(By.XPATH, "./td[1]").text.strip()
                    
                    href = link_element.get_attribute('href')
                    text = link_element.text
                    
                    if href and text:
                        links.append({
                            'url': href,
                            'text': text,
                            'code': code_mandat
                        })
                except Exception as e:
                    print(f"Erreur lors de l'extraction d'un lien: {e}")
                    continue
            
            print(f"Nombre de mandats trouvés : {len(links)}")
            
            for index, link_data in enumerate(links, 1):
                try:
                    code_mandat = link_data['code']
                    
                    if code_mandat in self.processed_mandats:
                        print(f"Mandat {code_mandat} déjà traité, passage au suivant...")
                        continue
                    
                    print(f"\nTraitement du mandat {index}/{len(links)}: {link_data['text']}")
                    
                    # Ouvrir un nouvel onglet
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    # Charger la page du mandat
                    self.driver.get(link_data['url'])
                    time.sleep(0.5)
                    
                    # Vérifier si l'accès est bloqué avec plusieurs méthodes
                    try:
                        # Attendre un court instant pour que la page se charge
                        time.sleep(0.5)
                        
                        # Essayer plusieurs méthodes pour détecter l'erreur
                        error_detected = False
                        ref_id = None
                        
                        # Méthode 1: Chercher le titre h3
                        try:
                            error_h3 = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'avez pas accès')]")
                            error_detected = True
                            ref_id = error_h3.text.split("Ref.ID:")[-1].strip() if "Ref.ID:" in error_h3.text else None
                        except:
                            pass
                        
                        # Méthode 2: Chercher la div d'alerte
                        if not error_detected:
                            try:
                                error_div = self.driver.find_element(By.CLASS_NAME, "t-Alert--danger")
                                error_detected = True
                                # Chercher le Ref.ID dans le texte de la div
                                error_text = error_div.text
                                if "Ref.ID:" in error_text:
                                    ref_id = error_text.split("Ref.ID:")[-1].split("\n")[0].strip()
                            except:
                                pass
                        
                        # Méthode 3: Chercher par le texte exact
                        if not error_detected:
                            try:
                                error_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Accès refusé par le contrôle de sécurité')]")
                                error_detected = True
                            except:
                                pass
                        
                        if error_detected:
                            print(f"Accès refusé pour le mandat {code_mandat}" + (f" (Ref.ID: {ref_id})" if ref_id else "") + " - marqué comme non valide")
                            
                            error_data = {
                                'code_mandat': code_mandat,
                                'titre_mandat': link_data['text'],
                                'url': link_data['url'],
                                'etat_mandat': 'Non valide - Accès refusé',
                                'date_verification': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if ref_id:
                                error_data['ref_id'] = ref_id
                            
                            error_data['message_erreur'] = 'Accès refusé par le contrôle de sécurité de la page'
                            
                            # Sauvegarder le mandat comme non valide
                            self.save_mandat(error_data)
                            
                            # Fermer l'onglet et continuer avec le prochain mandat
                            self.driver.close()
                            self.driver.switch_to.window(main_window)
                            continue
                            
                    except Exception as e:
                        print(f"Erreur lors de la vérification de l'accès: {str(e)}")
                    
                    # Si pas d'erreur d'accès, extraire les détails
                    details = self.extract_mandat_details()
                    
                    if details:
                        self.save_mandat(details)
                        print(f"Mandat {code_mandat} sauvegardé avec succès")
                    
                    # Fermer l'onglet et revenir à l'onglet principal
                    self.driver.close()
                    self.driver.switch_to.window(main_window)
                    
                except Exception as e:
                    print(f"Erreur lors du traitement du mandat {index}: {str(e)}")
                    try:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                        self.driver.switch_to.window(main_window)
                    except:
                        print("Erreur lors du retour à l'onglet principal")
                    continue
            
            return True
            
        except Exception as e:
            print(f"Erreur générale: {str(e)}")
            return False
        
    def extract_mandat_details(self):
        """Extrait les détails spécifiques d'un mandat"""
        try:
            wait = WebDriverWait(self.driver, 1)
            details = {}
            
            def extract_after_label(label):
                try:
                    xpath = f"//label[contains(text(), '{label}')]/../..//span[contains(@class, 'display_only')]"
                    element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    
                    if element:
                        return (element.get_attribute('innerText') or element.text).strip()
                        
                except:
                    try:
                        alt_xpath = f"//label[contains(text(), '{label}')]/../following-sibling::div//span"
                        element = self.driver.find_element(By.XPATH, alt_xpath)
                        if element:
                            return (element.get_attribute('innerText') or element.text).strip()
                    except:
                        pass
                return ''

            # Vérifier si la postulation est sur LaRuche
            try:
                # Chercher les éléments caractéristiques de la postulation sur LaRuche
                laruche_elements = [
                    "//div[contains(text(), 'Le document doit être en format .PDF')]",
                    "//label[contains(text(), 'Choisir un CV')]",
                    "//label[contains(text(), 'Choisir une lettre')]"
                ]
                
                # Chercher les éléments caractéristiques d'une postulation externe
                external_elements = [
                    "//div[contains(text(), 'Instruction de postulation')]"
                ]
                
                is_laruche = any(
                    self.driver.find_elements(By.XPATH, xpath)
                    for xpath in laruche_elements
                )
                
                is_external = any(
                    self.driver.find_elements(By.XPATH, xpath)
                    for xpath in external_elements
                )
                
                if is_laruche:
                    details['postulation_laruche'] = 'Oui'
                elif is_external:
                    details['postulation_laruche'] = 'Non'
                else:
                    details['postulation_laruche'] = 'Non'
                    
            except Exception as e:
                print(f"Erreur lors de la vérification du type de postulation: {str(e)}")
                details['postulation_laruche'] = 'Erreur de vérification'

            # Mapping des champs (même que précédemment)
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

            # Extraire tous les champs
            for field, label in fields.items():
                details[field] = self.clean_text(extract_after_label(label))

            # Cas spécial pour le site web
            try:
                site_web_xpath = "//label[contains(text(), 'Site Web')]/../following-sibling::div//a"
                site_web_element = self.driver.find_element(By.XPATH, site_web_xpath)
                if site_web_element:
                    details['site_web'] = site_web_element.get_attribute('href')
            except:
                pass

            details['url'] = self.driver.current_url
            return details

        except Exception as e:
            print(f"Erreur lors de l'extraction des détails: {str(e)}")
            return {}

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

    def clean_text(self, text):
        """Nettoie le texte des problèmes d'encodage multiples"""
        if not isinstance(text, str):
            return text
            
        try:
            # Décoder les HTML entities
            text = html.unescape(text)
            
            # Essayer de corriger l'encodage
            encodings = ['utf-8', 'latin1', 'iso-8859-1']
            for enc in encodings:
                try:
                    text = text.encode(enc).decode('utf-8')
                    break
                except:
                    continue
            
            # Nettoyer les espaces et caractères de contrôle
            text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            print(f"Erreur lors du nettoyage du texte: {str(e)}")
            return text

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