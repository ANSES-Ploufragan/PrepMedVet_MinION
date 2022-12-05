grep -E -i 'virid|viral' ../../Documents/PrepMedVet_analyses/taxid_lists/README.md | perl -p -e "s/^.*\(taxid: (\d+)\).*$/\1/" > patho_viral_taxid_list.txt

# get species taxids (leaves instead of general genus/order taxids)
# while IFS=read -r line; do
while read line; do
  echo "get leave taxids from $line"  
  get_species_taxids.sh -t $line > $line.taxids
done < patho_viral_taxid_list.txt

# perl -p -e 's/\n/,/' | perl -p -e 's/,$//' >


# to download refseq virus COMPLETE SEQUENCES only using viral pathogen taxids
# WARNING: maybe taxid must be leaves for ncbi, check perl script provided by ncbi to get leaves when providing any taxid
# -n for dry-run
conda activate ncbi-genome-download-0.3.1
ncbi-genome-download -s refseq --format fasta --assembly-levels complete --taxids patho_viral_taxid_list.txt -m genomes_metadata.tsv --flat-output viral -n


# phages mainly, but ok
ncbi-genome-download --format fasta -assembly-levels complete --taxids 10292.taxids -n viral

