import os

subset_pfam = lambda: os.system('''mkdir -p pfam_db
> pfam_db/Pfam-A_subset.hmm
> pfam_db/hmmfetch_errors_subset.log

while read -r hmm || [[ -n "$hmm" ]]; do
    hmm=$(echo "$hmm" | tr -d '\r' | xargs)
    [[ -z "$hmm" ]] && continue
    hmmfetch pfam_db/Pfam-A.hmm "$hmm" >> pfam_db/Pfam-A_subset.hmm 2>/dev/null || echo "$hmm" >> pfam_db/hmmfetch_errors_subset.log
done < data/Pfam-A_subset.txt

[ ! -f "pfam_db/Pfam-A_subset.hmm.ssi" ] && hmmfetch --index pfam_db/Pfam-A_subset.hmm || true
[ ! -f "pfam_db/Pfam-A_subset.hmm.h3p" ] && hmmpress -f pfam_db/Pfam-A_subset.hmm || true''')