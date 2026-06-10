#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
from scripts.downloader import download_queries
from scripts.setup_hmmer import setup_pfam
from scripts.pfam_subset_creator import subset_pfam
from scripts.analyzer import HmmscanParser
from scripts.logo_generator import generate_logo  # Nuevo import

def main():
    parser = argparse.ArgumentParser(description="Automatización de HMMER: Descarga, Escaneo, Análisis y Logos.")
    
    # --- ARGUMENTOS DEL PIPELINE ---
    parser.add_argument("--queries", help="Ruta al archivo de texto con IDs para correr el pipeline.")
    parser.add_argument("--db-mode", choices=['full', 'subset'], default='full', help="Elige la BD Pfam ('full' o 'subset').")
    parser.add_argument("--subset-file", help="Archivo para crear subconjunto. Requerido si --db-mode es 'subset'.")
    parser.add_argument("--no-cut-ga", action="store_true", help="Desactiva umbrales GA.")
    
    # --- ARGUMENTOS DE ANÁLISIS ---
    parser.add_argument("--analyze", type=str, help="ID de UniProt (ej. P00519) para analizar el .tbl.")
    parser.add_argument("--tbl-file", type=str, help="Ruta a un archivo .tbl ya existente (salta el escaneo).")
    
    # --- ARGUMENTOS DE GRAFICACIÓN ---
    parser.add_argument("--logo", type=str, help="Nombre del dominio Pfam (ej. SH2) para generar su HMM Logo en SVG.")

    args = parser.parse_args()
    
    # Validar que al menos se solicitó una acción
    if not any([args.queries, args.tbl_file, args.logo]):
        parser.error("Debes indicar una acción: '--queries' (escaneo), '--tbl-file' (análisis directo), o '--logo' (graficar dominio).")

    if args.tbl_file and args.queries:
        parser.error("Incompatibilidad: No uses '--queries' y '--tbl-file' juntos.")

    # ==========================================
    # DEFINIR LA BASE DE DATOS (Usada para escanear y/o sacar logos)
    # ==========================================
    db_path = "pfam_db/Pfam-A.hmm" if args.db_mode == 'full' else "pfam_db/Pfam-A_subset.hmm"

    # ==========================================
    # FLUJO 1: PIPELINE DE ESCANEO (Si hay --queries)
    # ==========================================
    out_tbl = None
    if args.queries:
        if args.db_mode == 'subset' and not args.subset_file:
            parser.error("--subset-file es obligatorio cuando --db-mode es 'subset'.")

        print("[1/4] Descargando secuencias...")
        download_queries(args.queries)

        print(f"[2/4] Configurando la base de datos en modo: {args.db_mode}...")
        if args.db_mode == 'full':
            setup_pfam()
        else:
            setup_pfam() 
            subset_pfam(args.subset_file)

        nombre_query = os.path.splitext(os.path.basename(args.queries))[0]
        os.makedirs("results", exist_ok=True)
        out_file = f"results/{nombre_query}_{args.db_mode}.txt"
        out_tbl = f"results/{nombre_query}_{args.db_mode}.tbl"

        print(f"[3/4] Ejecutando hmmscan contra {db_path}...")
        queries_fasta = "results/queries/queries.fasta"
        
        if not os.path.exists(queries_fasta):
            print(f"Error: No se encontró el archivo {queries_fasta}.")
            sys.exit(1)

        hmmscan_args = f"--tblout {out_tbl} -o {out_file}"
        if not args.no_cut_ga:
            hmmscan_args += " --cut_ga"

        comando_hmmscan = f"hmmscan {hmmscan_args} {db_path} {queries_fasta}"
        try:
            subprocess.run(comando_hmmscan, shell=True, check=True)
            print(f"      -> Resultados guardados en: {out_tbl}")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar hmmscan: {e}")
            sys.exit(1)

    # ==========================================
    # FLUJO 2: ANÁLISIS DE DATOS (Si hay --analyze)
    # ==========================================
    target_tbl = args.tbl_file if args.tbl_file else out_tbl
    if args.analyze:
        if not target_tbl:
            print("Error: No se especificó un archivo .tbl para analizar y no se corrió el pipeline.")
        elif not os.path.exists(target_tbl):
            print(f"Error: No se encontró el archivo {target_tbl}")
        else:
            print(f"\n[Análisis] Analizando ID: {args.analyze} en {target_tbl}...")
            parser_obj = HmmscanParser(target_tbl)
            parser_obj.parse()
            proteina = parser_obj.get_protein(args.analyze)
            proteina.print_summary()

    # ==========================================
    # FLUJO 3: GENERACIÓN DE LOGO (Si hay --logo)
    # ==========================================
    if args.logo:
        # Asegurarnos de que la BD existe antes de pedir el logo
        if not os.path.exists(db_path):
            print(f"\n[Logo] Preparando la base de datos requerida ({args.db_mode})...")
            setup_pfam()
            if args.db_mode == 'subset':
                subset_pfam(args.subset_file)
                
        generate_logo(args.logo, db_path)

if __name__ == "__main__":
    main()