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
            new_path = os.path.join(dir_name, f"{name}_en_claude{ext}")
            
            print(f"  Saving to {new_path}")
            wb.save(new_path)
            return True
        except Exception as e:
            print(f"❌ Failed to save {new_path}: {e}")
            return False

def main():
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "doris", "62092_sesa", "data", "calculations")
    
    if not os.path.exists(target_dir):
        print(f"❌ Target directory not found: {target_dir}")
        sys.exit(1)
    
    # Comprehensive Dictionary - expanded for full coverage
    replacements = {
        # ===== DOCUMENT TITLES & HEADERS =====
        "MEMORIA DE CÁLCULO DE TENSIÓN DE HALADO": "PULLING TENSION CALCULATION REPORT",
        "MEMORIA DE CÁLCULO": "CALCULATION REPORT",
        "MEMORIAS DE CÁLCULO": "CALCULATION REPORTS",
        "BASES DEL CÁLCULO": "CALCULATION BASIS",
        "BASES DEL CÁLCULO MKII": "MKII CALCULATION BASIS",
        "BASES DEL CÁLCULO HILLI": "HILLI CALCULATION BASIS",
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

        # ===== BUOYANCY/FLOTATION CALCULATIONS =====
        "CÁLCULO DE FLOTADORES HILLI-MKII": "HILLI-MKII BUOYANCY MODULES CALCULATION",
        "CÁLCULO DE FLOTADORES REQUERIDOS": "REQUIRED BUOYANCY MODULES CALCULATION",
        "CÁLCULO DE FLOTADORES": "BUOYANCY MODULES CALCULATION",
        "CÁLCULO DE LOS FLOTADORES REQUERIDOS": "CALCULATION OF REQUIRED BUOYANCY MODULES",
        "CON UN LASTRE DE CONCRETO": "WITH CONCRETE COATING",
        "Factor de Flotacion": "Buoyancy Factor",
        "Factor de flotación mínimo": "Minimum buoyancy factor",
        "Desplazamiento o empuje hidráulico del flotador": "Float hydraulic displacement or buoyancy",
        "Desplazamiento total": "Total displacement",
        "Desplazamiento unitario de tubería": "Pipe unit displacement",
        "Densidad estimada del poliuretano de los flotadores": "Estimated density of float polyurethane",
        "Densidad del poliuretano de los flotadores": "Density of float polyurethane",
        "Longitud Flotador": "Float Length",
        "Longitud flotador": "Float length",

        # ===== FRICTION & TENSION CALCULATIONS =====
        "CÁLCULO FUERZA DE FRICCIÓN EN SECTOR HORIZONTAL DEL TREN": "LAUNCHWAY HORIZONTAL SECTION FRICTION FORCE CALCULATION",
        "CÁLCULO FUERZA DE FRICCIÓN EN SECTOR INCLINADO DEL TREN": "LAUNCHWAY INCLINED SECTION FRICTION FORCE CALCULATION",
        "CÁLCULO FUERZA DE ARRASTRE EN EL MAR": "SEA DRAG FORCE CALCULATION",
        "CÁLCULO FUERZA RESISTENTA AL MOVIMIENTO": "MOVEMENT RESISTANCE FORCE CALCULATION",
        "TENSIÓN MÁXIMA DE HALADO": "MAXIMUM PULLING TENSION",
        "Fuerza de fricción del sector inclinado": "Inclined section friction force",
        "Fuerza fricción estática sector horizontal": "Horizontal section static friction force",
        "Fuerza total por friccion estática sector inclinado": "Total static friction force inclined section",
        "Fuerza total por fricción estática sector horizontal": "Total static friction force horizontal section",
        "Fuerza de arrastre de la línea en el mar": "Line drag force in sea",
        "Fuerza total de arrastre de la linea en el mar": "Total line drag force in sea",
        "Fuerza de arrastre en Kg-f": "Drag force in Kg-f",
        "Fuerza requerida de halado": "Required pulling force",
        "mínima capacidad del Winche": "minimum Winch capacity",
        "Coeficiente de fricción estático": "Static friction coefficient",
        "Coeficiente de resistencia media en el mar": "Average sea resistance coefficient",

        # ===== PIPE & COATING PROPERTIES =====
        "Peso unitario de la tubería": "Pipe unit weight",
        "Diametro exterior tubería": "Pipe outer diameter",
        "Diametro exterior": "Outer diameter",
        "Diámetro externo de la tubería": "Pipe outer diameter",
        "Diámetro externo de la camisa lastrada": "Coated jacket outer diameter",
        "Diámetro interno del lastre": "Coating inner diameter",
        "Espesor tubería": "Pipe thickness",
        "Espesor del lastre de concreto sobre la tubería": "Concrete coating thickness on pipe",
        "Ángulo de Inclinación": "Inclination Angle",
        "Longitud aproximada de la tubería hasta el PLEM": "Approximate pipe length to PLEM",
        "Longitud estimada de la tubería hasta el PLEM": "Estimated pipe length to PLEM",
        "con lastre": "with coating",

        # ===== DENSITY & MATERIAL PROPERTIES =====
        "Densidad del agua salada a 20°C (Superficie)": "Saltwater density at 20°C (Surface)",
        "Densidad del agua salada a 25°C (Superficie)": "Saltwater density at 25°C (Surface)",

        # ===== SHEET NAMES =====
        "Caratula_SESA": "SESA_Cover",
        "Caratula": "Cover",
        "Calculo TENSIONADOR": "TENSIONER Calculation",

        # ===== TECHNICAL TERMS - LONGER PHRASES FIRST =====
        "tren de lanzamiento": "launchway",
        "del primer tramo inclinado": "of the first inclined section",
        "del segundo tramo inclinado": "of the second inclined section",
        "concreto-neopreno de los rodillos": "roller concrete-neoprene",
        "Factor de seguridad por cargas perdidas": "Safety factor for lost loads",

        # ===== SINGLE WORD TECHNICAL TERMS =====
        "tubería": "pipe",
        "tuberías": "pipes",
        "Cálculos": "Calculations",
        "Calculo": "Calculation",
        "Cálculo": "Calculation",
        "Tensión": "Tension",
        "tensión": "tension",
        "TENSIONADOR": "TENSIONER",
        "Flotador": "Float",
        "flotador": "float",
        "FLOTADORES": "BUOYANCY MODULES",
        "Flotadores": "Floats",
        "flotadores": "floats",
        "Lastre": "Coating",
        "lastre": "coating",
        "LASTRE": "COATING",
        "lastrada": "coated",
        "lastrado": "coated",
        "Concreto": "Concrete",
        "concreto": "concrete",
        "CONCRETO": "CONCRETE",
        "Halado": "Pulling",
        "halado": "pulling",
        "HALADO": "PULLING",
        "Fricción": "Friction",
        "fricción": "friction",
        "Arrastre": "Drag",
        "arrastre": "drag",
        "Empuje": "Buoyancy",
        "empuje": "buoyancy",
        "Hidráulico": "Hydraulic",
        "hidráulico": "hydraulic",
        "Desplazamiento": "Displacement",
        "desplazamiento": "displacement",
        "REQUERIDOS": "REQUIRED",
        "Requeridos": "Required",
        "requerido": "required",
        "requeridos": "required",
        "Densidad": "Density",
        "densidad": "density",
        "Espesor": "Thickness",
        "espesor": "thickness",
        "Diámetro": "Diameter",
        "diámetro": "diameter",
        "Diametro": "Diameter",
        "diametro": "diameter",
        "Longitud": "Length",
        "longitud": "length",
        "Ángulo": "Angle",
        "ángulo": "angle",
        "Coeficiente": "Coefficient",
        "coeficiente": "coefficient",
        "Superficie": "Surface",
        "superficie": "surface",
        "Unitario": "Unit",
        "unitario": "unit",
        "Exterior": "Outer",
        "exterior": "outer",
        "externo": "external",
        "Externo": "External",
        "Interior": "Inner",
        "interior": "inner",
        "Interno": "Internal",
        "interno": "internal",
        "Horizontal": "Horizontal",
        "horizontal": "horizontal",
        "Inclinado": "Inclined",
        "inclinado": "inclined",
        "Inclinación": "Inclination",
        "inclinación": "inclination",
        "Vertical": "Vertical",
        "vertical": "vertical",
        "Sector": "Section",
        "sector": "section",
        "Tramo": "Segment",
        "tramo": "segment",
        "Estación": "Station",
        "estación": "station",
        "Resistencia": "Resistance",
        "resistencia": "resistance",
        "Resistente": "Resistant",
        "resistente": "resistant",
        "Capacidad": "Capacity",
        "capacidad": "capacity",
        "Fuerza": "Force",
        "fuerza": "force",
        "Peso": "Weight",
        "peso": "weight",
        "Gravedad": "Gravity",
        "gravedad": "gravity",
        "Rodillos": "Rollers",
        "rodillos": "rollers",
        "Camisa": "Jacket",
        "camisa": "jacket",
        "Poliuretano": "Polyurethane",
        "poliuretano": "polyurethane",
        "Estático": "Static",
        "estático": "static",
        "estática": "static",
        "Lanzamiento": "Launch",
        "lanzamiento": "launch",
        "Lanzador": "Launcher",
        "lanzador": "launcher",
        "Lanzado": "Launched",
        "lanzado": "launched",
        "Movimiento": "Movement",
        "movimiento": "movement",
        "Velocidad": "Velocity",
        "velocidad": "velocity",
        "Presión": "Pressure",
        "presión": "pressure",
        "Área": "Area",
        "área": "area",
        "Total": "Total",
        "total": "total",
        "Máximo": "Maximum",
        "máximo": "maximum",
        "Máxima": "Maximum",
        "máxima": "maximum",
        "Mínimo": "Minimum",
        "mínimo": "minimum",
        "Mínima": "Minimum",
        "mínima": "minimum",
        "Medio": "Average",
        "medio": "average",
        "Media": "Average",
        "media": "average",
        "Número": "Number",
        "número": "number",
        "Numero": "Number",
        "numero": "number",
        "Espaciamiento": "Spacing",
        "espaciamiento": "spacing",
        "Separación": "Separation",
        "separación": "separation",
        "Distanciamiento": "Spacing",
        "distanciamiento": "spacing",
        "Distribución": "Distribution",
        "distribución": "distribution",
        "Unidad": "Unit",
        "unidad": "unit",
        "Cantidad": "Quantity",
        "cantidad": "quantity",
        "Tamaño": "Size",
        "tamaño": "size",
        "Diseño": "Design",
        "diseño": "design",
        "Análisis": "Analysis",
        "análisis": "analysis",
        "Construcción": "Construction",
        "construcción": "construction",
        "Instalación": "Installation",
        "instalación": "installation",
        "Producción": "Production",
        "producción": "production",
        "Ejecución": "Execution",
        "ejecución": "execution",
        "Emisión": "Issue",
        "emisión": "issue",
        "Revisión": "Revision",
        "revisión": "revision",
        "Edición": "Edition",
        "edición": "edition",
        "Verificación": "Verification",
        "verificación": "verification",
        "Validación": "Validation",
        "validación": "validation",
        "Medición": "Measurement",
        "medición": "measurement",
        "Especificación": "Specification",
        "especificación": "specification",
        "Información": "Information",
        "información": "information",
        "Metodología": "Methodology",
        "metodología": "methodology",
        "Ingeniería": "Engineering",
        "ingeniería": "engineering",
        "Técnica": "Technical",
        "técnica": "technical",
        "Típica": "Typical",
        "típica": "typical",
        "Típico": "Typical",
        "típico": "typical",
        "Costero": "Coastal",
        "costero": "coastal",
        "Sumergido": "Submerged",
        "sumergido": "submerged",
        "Severo": "Severe",
        "severo": "severe",
        "Daño": "Damage",
        "daño": "damage",
        "Acero": "Steel",
        "acero": "steel",
        "Forjado": "Forged",
        "forjado": "forged",
        "Licuado": "Liquefied",
        "licuado": "liquefied",
        "Licuefacción": "Liquefaction",
        "licuefacción": "liquefaction",
        "Conexión": "Connection",
        "conexión": "connection",
        "Inertización": "Inerting",
        "inertización": "inerting",
        "Requerimiento": "Requirement",
        "requerimiento": "requirement",
        "Cumplimiento": "Compliance",
        "cumplimiento": "compliance",
        "Seguridad": "Safety",
        "seguridad": "safety",
        "Condición": "Condition",
        "condición": "condition",
        "Subsección": "Subsection",
        "subsección": "subsection",
        "Estándar": "Standard",
        "estándar": "standard",
        "Estándares": "Standards",
        "estándares": "standards",
        "Márgenes": "Margins",
        "márgenes": "margins",
        "Ilustración": "Illustration",
        "ilustración": "illustration",
        "Memoria": "Report",
        "memoria": "report",
        "Realización": "Completion",
        "realización": "completion",
        "República": "Republic",
        "república": "republic",
        "País": "Country",
        "país": "country",
        "Antecedente": "Background",
        "antecedente": "background",
        "Presente": "Present",
        "presente": "present",
        "Línea": "Line",
        "línea": "line",
        "Ítem": "Item",
        "ítem": "item",
        "Ítems": "Items",
        "ítems": "items",
        "Última": "Last",
        "última": "last",

        # ===== VERBS & VERB FORMS =====
        "Calcular": "Calculate",
        "calcular": "calculate",
        "Calculado": "Calculated",
        "calculado": "calculated",
        "calculará": "will calculate",
        "Determinar": "Determine",
        "determinar": "determine",
        "considerando": "considering",
        "Considerando": "Considering",
        "Proporcionado": "Provided",
        "proporcionado": "provided",
        "Extraído": "Extracted",
        "extraído": "extracted",
        "Vinculado": "Linked",
        "vinculado": "linked",
        "Asociado": "Associated",
        "asociado": "associated",
        "Denominado": "Named",
        "denominado": "named",
        "Dividido": "Divided",
        "dividido": "divided",
        "Controlado": "Controlled",
        "controlado": "controlled",
        "Transportado": "Transported",
        "transportado": "transported",
        "Está": "Is",
        "está": "is",
        "Están": "Are",
        "están": "are",
        "Estarán": "Will be",
        "estarán": "will be",
        "Será": "Will be",
        "será": "will be",
        "Serán": "Will be",
        "serán": "will be",
        "Podrá": "May",
        "podrá": "may",
        "efectuará": "will perform",

        # ===== PREPOSITIONS & CONNECTORS =====
        "Mediante": "By means of",
        "mediante": "by means of",
        "Posteriormente": "Subsequently",
        "posteriormente": "subsequently",
        "Directamente": "Directly",
        "directamente": "directly",
        "Respectivamente": "Respectively",
        "respectivamente": "respectively",
        "Aproximadamente": "Approximately",
        "aproximadamente": "approximately",
        "Continuación": "Following",
        "continuación": "following",
        "Durante": "During",
        "durante": "during",
        "Hacia": "Towards",
        "hacia": "towards",
        "Hasta": "Until",
        "hasta": "until",
        "Desde": "From",
        "desde": "from",
        "Según": "According to",
        "según": "according to",
        "Sobre": "On",
        "sobre": "on",
        "Bajo": "Under",
        "bajo": "under",
        "Algún": "Some",
        "algún": "some",
        "Cada": "Each",
        "cada": "each",
        "Entre": "Between",
        "entre": "between",
        "A través": "Through",
        "a través": "through",
        "Través": "Through",
        "través": "through",
        "Demás": "Other",
        "demás": "other",
        "Más": "More",
        "más": "more",
        "Menos": "Less",
        "menos": "less",
        "Como": "As",
        "como": "as",
        "Que": "That",
        "que": "that",
        "Sin": "Without",
        "sin": "without",
        "Con": "With",
        "con": "with",

        # ===== ADDITIONAL MISSING TERMS =====
        "documento": "document",
        "Documento": "Document",
        "flotación": "flotation",
        "Flotación": "Flotation",
        "lingada": "sling",
        "primera": "first",
        "Primera": "First",
        "segundo": "second",
        "Segunda": "Second",
        "mover": "move",
        "Mover": "Move",
        "friccioó": "friction",  # typo in source
        "caso": "case",
        "Caso": "Case",
        "solo": "only",
        "Solo": "Only",
        "usa": "uses",
        "cual": "which",
        "Cual": "Which",
        "define": "defines",
        "su": "its",
        "Sus": "Its",
        "mar": "sea",
        "Mar": "Sea",
        "es": "is",
        "mas": "more",
        "Mas": "More",

        # ===== COMMON SHORT WORDS (word boundary protected) =====
        "DE": "OF",
        "LA": "THE",
        "EL": "THE",
        "LOS": "THE",
        "LAS": "THE",
        "DEL": "OF THE",
        "EN": "IN",
        "POR": "BY",
        "PARA": "FOR",
        "UNA": "A",
        "UNO": "ONE",
        "UN": "A",
        "Y": "AND",
        "O": "OR",
    }

    translator = ExcelTranslator(replacements)
    
    try:
        # Exclude already-translated files (_en.xlsx, _en_gemini.xlsx, _en_claude.xlsx, _codex.xlsx)
        excluded_suffixes = ('_en.xlsx', '_en_gemini.xlsx', '_en_claude.xlsx', '_codex.xlsx')
        files = [f for f in os.listdir(target_dir) if f.endswith('.xlsx') and not f.endswith(excluded_suffixes)]
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
