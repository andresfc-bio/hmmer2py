import re

class HmmDomain:
    """Representa un dominio individual encontrado por hmmscan."""
    def __init__(self, target_name, accession, e_value, score, description):
        self.target_name = target_name
        self.accession = accession
        self.e_value = float(e_value)
        self.score = float(score)
        self.description = description

    def __str__(self):
        return f"- {self.target_name} ({self.accession}) | E-value: {self.e_value:.2e} | Score: {self.score} | Desc: {self.description}"

class ProteinAnalysis:
    """Agrupa todos los dominios de una proteína específica y permite su análisis."""
    def __init__(self, query_id):
        self.query_id = query_id
        self.domains = []

    def add_domain(self, domain):
        self.domains.append(domain)

    def get_best_domain(self):
        """Devuelve el dominio con el E-value más bajo."""
        if not self.domains:
            return None
        return min(self.domains, key=lambda d: d.e_value)

    def print_summary(self):
        """Imprime un resumen formateado del análisis en la terminal."""
        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS DE ANÁLISIS PARA: {self.query_id}")
        print(f"{'='*60}")
        
        if not self.domains:
            print("No se encontraron dominios significativos para este ID.")
            print(f"{'='*60}\n")
            return

        print(f"Total de dominios detectados: {len(self.domains)}")
        
        best = self.get_best_domain()
        print(f"\n🏆 MEJOR DOMINIO (Menor E-value):")
        print(f"   {best.target_name} (E-value: {best.e_value:.2e})")
        
        print("\n📋 LISTA COMPLETA DE DOMINIOS:")
        for dom in self.domains:
            print(f"   {dom}")
        print(f"{'='*60}\n")

class HmmscanParser:
    """Lee el archivo .tbl de salida de hmmscan y construye los objetos."""
    def __init__(self, filepath):
        self.filepath = filepath
        self.proteins = {}  # Diccionario: { 'P00519': ProteinAnalysis_Object }

    def parse(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                # Ignorar comentarios y líneas vacías
                if line.startswith('#') or not line.strip():
                    continue
                
                parts = line.split()
                # Asegurarnos de que la línea tiene las columnas esperadas de hmmscan
                if len(parts) < 19:
                    continue
                
                target_name = parts[0]
                target_acc = parts[1]
                query_name = parts[2]  # Ej: sp|P00519|ABL1_HUMAN
                
                # Extraer el ID puro de UniProt (Ej: P00519) usando expresiones regulares
                match = re.search(r'\|([A-Z0-9]+)\|', query_name)
                uniprot_id = match.group(1) if match else query_name
                
                e_value = parts[4]
                score = parts[5]
                # Reconstruir la descripción (puede contener espacios)
                description = " ".join(parts[18:])
                
                # Crear objeto dominio
                domain = HmmDomain(target_name, target_acc, e_value, score, description)
                
                # Agregarlo a la proteína correspondiente
                if uniprot_id not in self.proteins:
                    self.proteins[uniprot_id] = ProteinAnalysis(uniprot_id)
                self.proteins[uniprot_id].add_domain(domain)

    def get_protein(self, uniprot_id):
        """Devuelve el objeto ProteinAnalysis para un ID, o uno vacío si no existe."""
        return self.proteins.get(uniprot_id, ProteinAnalysis(uniprot_id))