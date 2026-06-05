import subprocess

def download_queries(archivo_queries):
    comandos = f'''
    mkdir -p results/queries && rm -f results/queries/failed_downloads.log results/queries/queries.fasta
    awk NF "{archivo_queries}" | while read -r id; do
    {{ [ -s "results/queries/$id.fasta" ] || wget -qO "results/queries/$id.fasta" "https://www.uniprot.org/uniprot/$id.fasta"; }} \\
        && grep -q '^>' "results/queries/$id.fasta" \\
        && cat "results/queries/$id.fasta" >> results/queries/queries.fasta \\
        || {{ echo "$id" >> results/queries/failed_downloads.log; rm -f "results/queries/$id.fasta"; }}
    done
    '''
    subprocess.run(comandos, shell=True, executable='/bin/bash')