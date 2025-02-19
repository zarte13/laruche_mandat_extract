import json
from pathlib import Path
import sys
from datetime import datetime

class MandatFilter:
    def __init__(self):
        self.mandats_file = "mandats.json"
        self.filtered_file = "mandats_filtered.json"

    def load_mandats(self):
        """Charge les mandats depuis le fichier JSON"""
        try:
            with open(self.mandats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Fichier {self.mandats_file} non trouvé")
            return []
        except json.JSONDecodeError:
            print(f"Erreur de lecture du fichier {self.mandats_file}")
            return []

    def filter_mandats(self, mandats):
        """Filtre les mandats selon les critères"""
        filtered_mandats = []
        
        for mandat in mandats:
            try:
                # Vérifier si le mandat est valide (pas d'accès refusé)
                if mandat.get('etat_mandat') == 'Non valide - Accès refusé':
                    continue
                
                # Vérifier si la postulation est sur LaRuche
                if mandat.get('postulation_laruche') != 'Oui':
                    continue
                
                # Vérifier si le mandat est toujours ouvert
                date_limite_str = mandat.get('date_limite')
                if date_limite_str:
                    try:
                        # Convertir la date limite en objet datetime
                        date_limite = datetime.strptime(date_limite_str, '%d-%m-%Y')
                        if date_limite < datetime.now():
                            continue
                    except ValueError:
                        print(f"Format de date invalide pour le mandat {mandat.get('code_mandat')}: {date_limite_str}")
                
                # Si toutes les conditions sont remplies, ajouter le mandat à la liste filtrée
                filtered_mandats.append(mandat)
                
            except Exception as e:
                print(f"Erreur lors du filtrage du mandat {mandat.get('code_mandat')}: {str(e)}")
                continue
        
        return filtered_mandats

    def save_filtered_mandats(self, filtered_mandats):
        """Sauvegarde les mandats filtrés dans un nouveau fichier"""
        try:
            with open(self.filtered_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_mandats, f, ensure_ascii=False, indent=2)
            print(f"Mandats filtrés sauvegardés dans {self.filtered_file}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des mandats filtrés: {str(e)}")

    def print_summary(self, all_mandats, filtered_mandats):
        """Affiche un résumé des résultats"""
        print("\nRésumé du filtrage :")
        print(f"Nombre total de mandats : {len(all_mandats)}")
        print(f"Nombre de mandats filtrés : {len(filtered_mandats)}")
        
        # Afficher les détails des mandats retenus
        print("\nMandats retenus :")
        for mandat in filtered_mandats:
            print(f"\nCode: {mandat.get('code_mandat')}")
            print(f"Titre: {mandat.get('titre_mandat')}")
            print(f"Date limite: {mandat.get('date_limite')}")
            print(f"Employeur: {mandat.get('employeur')}")
            print("-" * 50)

    def run(self):
        """Exécute le processus de filtrage"""
        print("Début du filtrage des mandats...")
        
        # Charger les mandats
        all_mandats = self.load_mandats()
        if not all_mandats:
            print("Aucun mandat à traiter")
            return
        
        # Filtrer les mandats
        filtered_mandats = self.filter_mandats(all_mandats)
        
        # Sauvegarder les résultats
        self.save_filtered_mandats(filtered_mandats)
        
        # Afficher le résumé
        self.print_summary(all_mandats, filtered_mandats)

def main():
    filter = MandatFilter()
    filter.run()

if __name__ == "__main__":
    main()