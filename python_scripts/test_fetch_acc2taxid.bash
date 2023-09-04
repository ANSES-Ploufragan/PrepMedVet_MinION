#!/bin/bash
# A00002 X53307 ok with db nuccore
for ACC in GCF_000001215 GCF_000001405
do
   echo -n -e "$ACC\t"
   curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id=${ACC}&rettype=taxid&retmode=xml" # |\
#   grep TSeq_taxid # |\
#   cut -d '>' -f 2 |\
#   cut -d '<' -f 1 |\
#   tr -d "\n"
   echo
done
