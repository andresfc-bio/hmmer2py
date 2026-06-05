import os

setup_pfam = lambda: os.system('''mkdir -p pfam_db && cd pfam_db
[ ! -f "Pfam-A.hmm" ] && wget -nc ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz && gunzip Pfam-A.hmm.gz || true
[ ! -f "Pfam-A.hmm.ssi" ] && hmmfetch --index Pfam-A.hmm || true
[ ! -f "Pfam-A.hmm.h3p" ] && hmmpress -f Pfam-A.hmm || true''')