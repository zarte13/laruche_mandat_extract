import json
import requests
import time
from pathlib import Path
from typing import Dict, List

class MotivationLetterGenerator:
    def __init__(self):
        self.filtered_mandats_file = "mandats_filtered.json"
        self.output_file = "lettres_motivation.json"
        self.api_key = self.load_api_key()
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.system_prompt ="""Tu es un expert en rédaction de lettres de motivation pour Philippe Lebel, étudiant en génie mécanique à Polytechnique Montréal.

        PROFIL DU CANDIDAT :
        - Nom: Philippe Lebel
        - Formation: Génie mécanique à Polytechnique Montréal
        - Expériences clés: Stagiaire en freinage de train – Alstom, Saint-Bruno-de-Montarville (2024)
	Optimisation des performances de freinage ferroviaire par analyse statistique de données (méthodologie PFMEA)
	Conduite d'études de cas sur le REM incluant diagnostics, essais nocturnes et analyses avec DEWESoft 
	Développement d'un programme Python pour l'automatisation du monitoring des systèmes de compression d'air.
Directeur technique et co-fondateur – Société technique Zenith / Polytechnique Montréal (2024-)
	Direction technique d'une équipe de 40+ personnes dans le développement de systèmes robotiques aériens
	Supervision de l'intégration des systèmes embarqués incluant l’utilisation de simulation Gazebo puis implémentation dans la réalité et validation des choix technologiques
	Validation de tolérances géométriques sur pièces critiques sur pièce usinées et imprimé en 3D
Membre de l’équipe drone – Société technique Polyorbite / Polytechnique Montréal (2023)
	Conception et fabrication rapide d’un drone de cartographie en moins de 3 mois
	Développement et implémentation de systèmes de contrôle de vol et protocoles
	Utilisation de SOLIDWORKS et de l'impression 3D pour la conception et la fabrication de composants structurels optimisés du drone.

        - Compétences techniques: 	Programmation (Python, Matlab, Simulink)
	Bases de données (SQL, Azure, Dataverse),
	Conception CAO (SolidWorks, CATIA), 
	Simulation FEM/CFD (Solidworks Simulation & Abaqus).
	Vibrations, connaissance en composites et tolérancement géométrique.


        DIRECTIVES DE RÉDACTION :
        1. Format:
           - Langue: Français formel
           - Longueur: 3/4 page
           - Structure: Introduction, corps, conclusion
           - Possibilité d'utiliser des bullet points (un seul niveau)

        2. Contenu:
           - Personnalisation selon le poste cible
           - Pas de références (ex: Ref: C-GE-470)
           - Signature: "Cordialement, 
Philippe Lebel"
           - Ton professionnel et engageant

        3. Structure requise:
           - Objet: Clair et concis
           - Introduction: Accroche forte
           - Corps: Alignement expériences/exigences
           - Conclusion: Call-to-action engageant

        4. À éviter:
           - Informations non présentes dans les exemples
           - Bullet points imbriqués
           - Références de poste
           - Longueur excessive

        EXEMPLES DE RÉFÉRENCE:
        À l’équipe de recrutement de Collineo,
Actuellement étudiant en génie mécanique à Polytechnique Montréal, je suis enthousiaste à l’idée de rejoindre votre équipe dans le cadre du mandat « Inspection pales éolienne robotisée » . Votre expertise en robotique appliquée à l’inspection des éoliennes et votre approche structurée en rotations (2 semaines sur site / 1 semaine de congé) correspondent parfaitement à mon goût pour les défis techniques exigeants et les environnements de travail dynamiques.
Mon expérience terrain et ma polyvalence : des atouts pour vos projets
Chez Alstom, lors des essais nocturnes du REM, j’ai alterné analyses techniques en journée et interventions sur site la nuit, en respectant des protocoles de sécurité stricts. Cette expérience m’a appris à m’adapter à des horaires variables tout en maintenant une rigueur technique, un atout pour vos journées pouvant atteindre 12 heures selon les conditions météorologiques.
Chez Zenith, j’ai piloté des tests de drones dans des zones reculées soumises à des vents violents. Cette immersion en contexte extrême m’a permis de développer une forte débrouillardise pour résoudre des problèmes logistiques ou techniques sous pression, tout en collaborant avec des équipes multidisciplinaires — une compétence cruciale pour travailler en binôme ou en groupe sur vos sites.
Enfin, lors de mon stage chez Trimatex, j’ai aidé à valider des assemblages critiques directement sur des chantiers, combinant inspections terrain et travail de bureau. Cette capacité à alterner entre précision technique (analyse de données, utilisation de logiciels) et efforts physiques prolongés sera un atout pour vos missions d’inspection robotisée et d’entretien des équipements en Gaspésie.
Pourquoi Collineo ?
Votre innovation dans l’automatisation des inspections éoliennes résonne avec mes projets académiques en robotique autonome et mes compétences en analyse de données (Python, SQL). Ma curiosité pour les technologies émergentes, comme les systèmes hydrogène chez Exocet, s’aligne avec votre vision d’outils automatisés pour la transition énergétique.
Mobilité: Permis de conduire valide, carte ASP Construction et expérience en logistique terrain (Alstom, Zenith) me permettront de m’intégrer rapidement à vos équipes.
Physique et mentale : Habitué aux déploiements exigeants, je suis motivé à contribuer à vos rotations de 2 semaines, avec des journées pouvant s’étendre jusqu’à 12 heures.
Je reste à votre disposition pour un entretien et vous remercie de votre considération.
Cordialement,
Philippe Lebel

Cher M. Aymeric Guy et équipe Modulate Technologies,
Votre mission de révolutionner le traitement de la scoliose par l'innovation technologique m'inspire profondément, car j’ai plusieurs membres de ma famille qui sont affectés par la scoliose. En tant qu'étudiant en génie mécanique passionné par l'impression 3D et les systèmes embarqués, je suis enthousiaste à l'idée de contribuer au développement de vos orthèses intelligentes.
Ce que j'apporte à votre projet innovant :
Expertise en Impression 3D et Matériaux
Expérience approfondie avec différents matériaux (PLA, TPU, Matériaux renforcés au composites, etc.)
Maîtrise des technologies FDM et SLS
Compréhension des contraintes de fabrication et d'intégration mécanique
Systèmes Embarqués et Capteurs
Développement de projets avec ESP32 et microcontrôleurs similaires
Expérience en communication BLE et acquisition de données
Programmation d'interfaces de visualisation en temps réel
Conception et Prototypage
Modélisation 3D et CAO pour optimisation de pièces
Intégration mécanique-électronique
Documentation technique rigoureuse et méthodique
Alignement avec vos besoins spécifiques :
Circuit embarqué : Mon expérience avec l'ESP32 et les protocoles de communication sans fil me permettront de développer rapidement votre système de monitoring.
Intégration mécanique : Ma connaissance approfondie de l'impression 3D facilitera l'incorporation des capteurs tout en respectant vos contraintes de conception.
Interface utilisateur : Mes compétences en programmation permettront de créer une visualisation 3D intuitive des données de pression.
En tant que personne autodidacte et proactive, je m'épanouis dans l'environnement dynamique des startups. Mon projet universitaire de système de monitoring environnemental démontre ma capacité à gérer des projets complexes combinant hardware et software.
Je suis particulièrement motivé par l'impact direct que ce projet aura sur la qualité de vie des patients, et je suis prêt à m'investir pleinement dans cette mission dès mai 2025.
Je reste à votre disposition pour un entretien et vous remercie de l'attention portée à ma candidature.
Cordialement,
Philippe Lebel


        Pour chaque nouvelle demande:
        1. Analyser les exigences du poste
        2. Sélectionner les expériences pertinentes des exemples
        3. Créer une lettre personnalisée
        4. Vérifier la conformité aux directives
        """
        
    def load_api_key(self) -> str:
        """Charge la clé API depuis un fichier de configuration"""
        try:
            with open('config/config.ini', 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        return line.split('=')[1].strip()
        except Exception as e:
            raise Exception(f"Erreur lors du chargement de la clé API: {str(e)}")

    def load_filtered_mandats(self) -> List[Dict]:
        """Charge les mandats filtrés depuis le fichier JSON"""
        try:
            with open(self.filtered_mandats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Erreur lors du chargement des mandats filtrés: {str(e)}")

    def generate_letter(self, mandat: Dict) -> Dict:
        """Génère une lettre de motivation pour un mandat donné"""
        try:
            # Préparer le contenu pour le prompt
            job_content = f"""
            Titre du poste: {mandat.get('titre_mandat', '')}
            Employeur: {mandat.get('employeur', '')}
            Exigences: {mandat.get('exigences_mandat', '')}
            Description du poste: {mandat.get('description_mandat', '')}
            """

            # Préparer les headers et le payload
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "o3-mini",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": job_content}
                ],
            }

            # Faire la requête à l'API
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                response_data = response.json()
                letter_content = response_data['choices'][0]['message']['content']
                
                return {
                    "code_mandat": mandat.get('code_mandat'),
                    "employeur": mandat.get('employeur'),
                    "url": mandat.get('url'),
                    "lettre_de_motivation": letter_content
                }
            else:
                print(f"Erreur API ({response.status_code}): {response.text}")
                return None

        except Exception as e:
            print(f"Erreur lors de la génération de la lettre pour le mandat {mandat.get('code_mandat')}: {str(e)}")
            return None

    def save_letter(self, letter: Dict):
        """Sauvegarde une lettre dans le fichier JSON"""
        try:
            # Charger les lettres existantes ou créer une nouvelle liste
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    letters = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                letters = []
            
            # Ajouter la nouvelle lettre
            letters.append(letter)
            
            # Sauvegarder toutes les lettres
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(letters, f, ensure_ascii=False, indent=2)
            
            print(f"Lettre pour le mandat {letter['code_mandat']} sauvegardée")
        
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la lettre: {str(e)}")

    def run(self):
        """Exécute le processus de génération des lettres"""
        print("Début de la génération des lettres de motivation...")
        
        # Charger les mandats filtrés
        mandats = self.load_filtered_mandats()
        print(f"Nombre de mandats à traiter: {len(mandats)}")

        # Générer et sauvegarder les lettres une par une
        success_count = 0
        for i, mandat in enumerate(mandats, 1):
            print(f"\nTraitement du mandat {i}/{len(mandats)}: {mandat.get('code_mandat')}")
            
            letter = self.generate_letter(mandat)
            if letter:
                # Sauvegarder immédiatement la lettre
                self.save_letter(letter)
                success_count += 1
                print(f"Lettre générée et sauvegardée avec succès")
            
            # Pause pour éviter de dépasser les limites de l'API
            time.sleep(0.5)

        print(f"\nGénération terminée. {success_count} lettres générées et sauvegardées.")

def main():
    generator = MotivationLetterGenerator()
    generator.run()

if __name__ == "__main__":
    main()