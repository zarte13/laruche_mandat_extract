from fpdf import FPDF
import json
import os
import time
from typing import Dict, List
from fpdf.enums import Align

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Ajout de la police DejaVu
        self.add_font("DejaVu", "", "ttf/DejaVuSansCondensed.ttf", uni=True)
        self.add_font("DejaVu", "B", "ttf/DejaVuSansCondensed-Bold.ttf", uni=True)
        self.add_font("DejaVu", "I", "ttf/DejaVuSansCondensed-Oblique.ttf", uni=True)

    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 5, '', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_bullet_text(self, text, indent=10):
        """Ajoute du texte avec un bullet point"""
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(5, 5, "•", 0, 0)
        self.set_x(x + indent + 8)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def add_paragraph(self, text, line_height=6):
        """Ajoute un paragraphe de texte"""
        self.multi_cell(0, line_height, text)
        self.ln(2)

class PDFGenerator:
    def __init__(self):
        self.input_file = "lettres_motivation.json"
        self.output_dir = "lettres_de_motivation"
        
        self.pdf_config = {
            'font_family': 'DejaVu',
            'font_size_title': 14,
            'font_size_body': 11,
            'line_height': 6,
            'paragraph_spacing': 2,
            'margin_left': 20,
            'margin_right': 20,
            'margin_top': 20,
            'margin_bottom': 20
        }
        
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_text(self, text: str) -> str:
        """Nettoie le texte pour le rendre compatible avec FPDF"""
        char_mapping = {
            '–': '-',
            '—': '-',
            "'": "'",
            '"': '"',
            '"': '"',
            '…': '...',
            '\u2013': '-',
            '\u2014': '-',
            '\u2018': "'",
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
            '\u2022': '•',
            '\u2026': '...',
            '\u00A0': ' ',
            '\u202F': ' ',
        }
        
        for old, new in char_mapping.items():
            text = text.replace(old, new)
            
        return text

    def create_pdf(self, letter_data: Dict) -> str:
        """Crée un fichier PDF formaté pour la lettre de motivation"""
        try:
            pdf = CustomPDF()
            pdf.add_page()
            pdf.set_margins(
                self.pdf_config['margin_left'],
                self.pdf_config['margin_top'],
                self.pdf_config['margin_right']
            )
            
            # Ajouter la date
            pdf.set_font('DejaVu', '', self.pdf_config['font_size_body'])
            pdf.cell(0, self.pdf_config['line_height'], time.strftime("%d/%m/%Y"), 0, 1, 'R')
            pdf.ln(5)
            
            # Corps de la lettre
            pdf.set_font('DejaVu', '', self.pdf_config['font_size_body'])
            
            clean_letter = self.clean_text(letter_data['lettre_de_motivation'])
            paragraphs = clean_letter.split('\n')
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Vérifier si c'est un bullet point (commence par •)
                    if '•' in paragraph:
                        text = paragraph.strip().replace('•', '').strip()
                        pdf.add_bullet_text(text)
                    else:
                        pdf.add_paragraph(
                            paragraph.strip(),
                            line_height=self.pdf_config['line_height']
                        )
            
            safe_employer = "".join(x for x in letter_data['employeur'] if x.isalnum() or x in (' ', '-', '_'))
            filename = f"{self.output_dir}/lettre_motivation_{safe_employer}_{letter_data['code_mandat']}.pdf"
            
            pdf.output(filename)
            return filename
            
        except Exception as e:
            print(f"Erreur lors de la création du PDF pour le mandat {letter_data['code_mandat']}: {str(e)}")
            return None

    def load_letters(self) -> List[Dict]:
        """Charge les lettres depuis le fichier JSON"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des lettres: {str(e)}")
            return []

    def generate_all_pdfs(self):
        """Génère les PDFs pour toutes les lettres"""
        letters = self.load_letters()
        if not letters:
            print("Aucune lettre trouvée dans le fichier JSON")
            return

        print(f"Génération de {len(letters)} PDFs...")
        
        for i, letter in enumerate(letters, 1):
            print(f"\nTraitement de la lettre {i}/{len(letters)} - Mandat: {letter['code_mandat']}")
            pdf_path = self.create_pdf(letter)
            
            if pdf_path:
                print(f"PDF créé avec succès: {pdf_path}")
            else:
                print(f"Échec de la création du PDF pour le mandat {letter['code_mandat']}")

def main():
    generator = PDFGenerator()
    generator.generate_all_pdfs()

if __name__ == "__main__":
    main()