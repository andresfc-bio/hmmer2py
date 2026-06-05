#!/home/x/miniforge3/envs/b/bin/python
import argparse
from scripts.downloader import download_queries

def main():
    parser = argparse.ArgumentParser(description="Descarga secuencias en formato FASTA desde UniProt.")
    
    parser.add_argument(
        "--queries", 
        required=True, 
        help="Ruta al archivo de texto con los IDs (ej. queries.txt)"
    )
    
    args = parser.parse_args()
    
    download_queries(args.queries)

if __name__ == "__main__":
    main()