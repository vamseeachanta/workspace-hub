import os
import sys
import openpyxl
import re
from typing import Dict, List, Tuple

class ExcelTranslator:
    """Handles translation of Excel files using a dictionary-based approach with regex optimization."""

    def __init__(self, replacements: Dict[str, str]):
        """
        Initialize the translator with a dictionary of replacements.
        
        Args:
            replacements: Dictionary mapping source terms to target terms.
        """
        self.replacements = replacements
        self.compiled_patterns: List[Tuple[re.Pattern, str]] = self._compile_patterns()

    def _compile_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """
        Pre-compile regex patterns for efficiency.
        Sorts replacements by length (longest first) to avoid partial matches of substrings.
        Uses word boundaries for short words (< 4 chars).
        """
        sorted_replacements = sorted(self.replacements.items(), key=lambda x: len(x[0]), reverse=True)
        compiled = []
        
        for span, eng in sorted_replacements:
            if len(span) < 4:
                # Word boundary for short words to prevent "DE" matching inside "CODE"
                pattern = re.compile(r'\b' + re.escape(span) + r'\b', re.IGNORECASE)
            else:
                # Standard case-insensitive replacement for longer phrases
                pattern = re.compile(re.escape(span), re.IGNORECASE)
            compiled.append((pattern, eng))
            
        return compiled

    def translate_text(self, text: str) -> str:
        """
        Translate a single string using pre-compiled patterns.
        
        Args:
            text: Input string.
            
        Returns:
            Translated string.
        """
        if not isinstance(text, str):
            return text
        
        for pattern, eng in self.compiled_patterns:
            text = pattern.sub(eng, text)
            
        return text

    def process_file(self, file_path: str) -> bool:
        """
        Process a single Excel file.
        
        Args:
            file_path: Path to the .xlsx file.
            
        Returns:
            True if successful, False otherwise.
        """
        print(f"Processing {file_path}...")
        try:
            wb = openpyxl.load_workbook(file_path)
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
            return False

        # Translate Sheet Names
        for sheet in wb.worksheets:
            new_title = self.translate_text(sheet.title)
            # Excel sheet name limits: 31 chars, no invalid chars
            if len(new_title) > 31:
                 new_title = new_title[:31]
            
            if new_title != sheet.title:
                try:
                    sheet.title = new_title
                except ValueError:
                    print(f"  ⚠️ Could not rename sheet '{sheet.title}' to '{new_title}' (likely duplicate or invalid)")

            # Translate Cell Values
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.data_type == 's': # String
                        new_value = self.translate_text(cell.value)
                        if new_value != cell.value:
                            cell.value = new_value

        # Save as new file
        try:
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            new_path = os.path.join(dir_name, f"{name}_en{ext}")
            
            print(f"  Saving to {new_path}")
            wb.save(new_path)
            return True
        except Exception as e:
            print(f"❌ Failed to save {new_path}: {e}")
            return False

def main():
    target_dir = "/mnt/github/workspace-hub/doris/62092_sesa/data/calculations"
    
    if not os.path.exists(target_dir):
        print(f"❌ Target directory not found: {target_dir}")
        sys.exit(1)
    
    # Comprehensive Dictionary
    replacements = {
        "MEMORIA DE CÁLCULO DE TENSIÓN DE HALADO": "PULLING TENSION CALCULATION REPORT",
        "MEMORIA DE CÁLCULO": "CALCULATION REPORT",
        "BASES DEL CÁLCULO": "CALCULATION BASIS",
        "Peso unitario de la tubería": "Pipe unit weight",
        "Diametro exterior tubería": "Pipe outer diameter",
        "Diametro exterior": "Outer diameter",
        "Ángulo de Inclinación": "Inclination Angle",
        "Espesor tubería": "Pipe thickness",
        "Espesor": "Thickness",
        "con lastre": "with coating",
        "DOC. N°": "DOC. NO.",
        "PAGINA": "PAGE",
        "REVISION": "REVISION",
        "INDICE": "TABLE OF CONTENTS",
        "OBJETIVO": "OBJECTIVE",
        "DOCUMENTOS Y ESTANDARES DE REFERENCIA": "REFERENCE DOCUMENTS AND STANDARDS",
        "DOCUMENTOS DE REFERENCIA": "REFERENCE DOCUMENTS",
        "ESTÁNDARES INTERNACIONALES": "INTERNATIONAL STANDARDS",
        "ANTECEDENTE DEL PROYECTO": "PROJECT BACKGROUND",
        "PREMISAS": "ASSUMPTIONS",
        "CÁLCULO DE FLOTADORES HILLI-MKII": "HILLI-MKII BUOYANCY MODULES CALCULATION",
        "CÁLCULO DE FLOTADORES": "BUOYANCY MODULES CALCULATION",
        "CÁLCULO DE LOS FLOTADORES REQUERIDOS": "CALCULATION OF REQUIRED BUOYANCY MODULES",
        "CON UN LASTRE DE CONCRETO": "WITH CONCRETE COATING",
        "MEMORIAS DE CÁLCULO": "CALCULATION REPORTS",
        "Caratula_SESA": "SESA_Cover",
        "Caratula": "Cover",
        "Calculo TENSIONADOR": "TENSIONER Calculation",
        "Calculo": "Calculation",
        "Cálculo": "Calculation",
        "TENSIONADOR": "TENSIONER",
        "tubería": "pipe",
        "del primer tramo inclinado": "of the first inclined section",
        "del segundo tramo inclinado": "of the second inclined section",
        "tren de lanzamiento": "launchway",
        "DE TENSION": "OF TENSION",
        "DE HALADO": "OF PULLING",
        "FLOTADORES": "BUOYANCY MODULES",
        "REQUERIDOS": "REQUIRED",
        "LASTRE": "COATING",
        "CONCRETO": "CONCRETE",
        # Short words - now safe due to regex boundary check
        "DE": "OF",
        "LA": "THE",
        "EL": "THE",
        "DEL": "OF THE",
        "EN": "IN",
        "POR": "BY",
        "PARA": "FOR",
    }

    translator = ExcelTranslator(replacements)
    
    try:
        files = [f for f in os.listdir(target_dir) if f.endswith('.xlsx') and not f.endswith('_en.xlsx')]
    except Exception as e:
        print(f"❌ Error listing files in {target_dir}: {e}")
        sys.exit(1)
        
    if not files:
        print(f"ℹ️ No eligible .xlsx files found in {target_dir}")
        return

    success_count = 0
    for f in files:
        file_path = os.path.join(target_dir, f)
        if translator.process_file(file_path):
            success_count += 1
            
    print(f"\n✅ Completed! Translated {success_count}/{len(files)} files.")

if __name__ == "__main__":
    main()
