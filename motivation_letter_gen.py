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
        self.system_prompt = """
        Tu es un expert en rédaction de lettres de motivation. 
        Analyse le poste fourni et crée une lettre de motivation personnalisée et professionnelle. Tu peux mettre mon nom: Philippe Lebel, à la fin. Et aussi tu peux finir la lettre avec Cordialement,
        La lettre doit être en français, formelle, et adaptée spécifiquement aux exigences et à la description du poste. 
        Inclus une introduction forte, un corps qui fait le lien entre tes compétences et les exigences, et une conclusion engageante. Tu peux aussi utiliser des bullets points pour rendre le contenu un peu plus ligible, sans trop exagéré. Garde la longueur à 3/4 d'une page.
        Voici deux exemple de lettre de motivation d'on tu peux te basé pour t'inspiré des expériences pertinente, mais n'invente pas de nouvelles expériences:
        1.Objet : Candidature - Stage en R&D
Cher service des ressources humaines de Pelican International,
En tant qu'étudiant en génie mécanique à Polytechnique Montréal, votre recherche d'un stagiaire R&D résonne particulièrement avec mon parcours en développement de produits et en analyse mécanique. La réputation d'excellence de Pelican dans l'industrie nautique et votre engagement envers l'innovation continue m'attirent particulièrement.
Mon expérience s'aligne directement avec vos besoins en R&D :
Analyse et Tests de Produits
Chez Alstom : Optimisation des performances de freinage par analyse statistique (PFMEA) et conduite d'essais nocturnes
Sur le projet de drone Polyorbite : Validation rigoureuse des tolérances géométriques sur pièces critiques
Expérience en analyse de stress, fatigue et tests fonctionnels sur composants imprimés 3D
Conception et Documentation Technique
Développement d'un Part Picker robotisé : Conception itérative sous SolidWorks avec optimisation des dimensions critiques
Maîtrise des outils de CAO pour mises en plan et définition des tolérances
Gestion de Projets et Coordination
Direction technique d'une équipe de 40+ personnes chez Zenith
Expérience en rédaction de rapports d'analyse et recommandations techniques
Réalisations Pertinentes :
Optimisation de composants structurels avec analyse FEA pour le drone Polyorbite
Développement de protocoles de test rigoureux pour validation de systèmes complexes
Intégration réussie de systèmes mécaniques et électroniques dans des environnements exigeants
Je suis particulièrement motivé par l'opportunité de :
Contribuer à l'évaluation et l'optimisation de vos produits nautiques
Appliquer mes compétences en analyse mécanique et validation de prototypes
Participer au développement de solutions innovantes dans un environnement dynamique
Mon expérience démontre ma capacité à gérer des projets complexes, à effectuer des analyses rigoureuses et à documenter efficacement les résultats - des compétences essentielles pour ce stage en R&D.
Je suis disponible pour commencer dès mai 2025 et reste à votre disposition pour un entretien.
Cordialement,
Philippe Lebel
2.À l’équipe de recrutement de Collineo,
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