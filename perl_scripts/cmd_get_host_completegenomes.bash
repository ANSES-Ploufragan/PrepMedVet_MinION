# vertebrates mammalian: 129 dont sus scrofa
ncbi-genome-download  -s refseq --format fasta --assembly-levels complete,chromosome -m /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ncbigd_meta.tsv --flat-output --output-folder /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ vertebrate_mammalian -n
# vertebrate_other: 251
ncbi-genome-download  -s refseq --format fasta --assembly-levels complete,chromosome -m /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ncbigd_meta.tsv --flat-output --output-folder /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ vertebrate_other -n
# invertebrate: 189 dont anophele
ncbi-genome-download  -s refseq --format fasta --assembly-levels complete,chromosome -m /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ncbigd_meta.tsv --flat-output --output-folder /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ invertebrate -n
# plant: 126
ncbi-genome-download  -s refseq --format fasta --assembly-levels complete,chromosome -m /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ncbigd_meta.tsv --flat-output --output-folder /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ plant -n


# all previous: 692
ncbi-genome-download  -s refseq --format fasta --assembly-levels complete,chromosome -m /home/touzain/Téléchargements/tmp_PrepMedVet_Sus_scrofa/ncbigd_meta.tsv --flat-output --output-folder /media/dd_travail/db/host_complete_genomes2/ vertebrate_mammalian,vertebrate_other,invertebrate,plant -n

# in the directory where fna.gz files were downloaded for the db
ls *gz | perl -p -e "s/^(GCF_\d+\.\d+)_.*\.fna\.gz$/\1/" > /media/data/ANSES/PrepMedVet_analyses/taxid_lists/host_complete_genomes_accnr.txt

# script python
./accnr2accnr_taxid.py -i ../taxid_lists/host_complete_genomes_accnr.txt -o ../taxid_lists/host_complete_genomes_accnr_taxid.tsv -d ../taxid_lists/host_complete_genomes_accnr_taxid_missing.txt

# completion manuelle quand manquant taxid

cat ../taxid_lists/host_complete_genomes_accnr_taxid.tsv | column --table --table-order 2,1 > ../taxid_lists/host_complete_genomes_taxid_accnr.tsv

# creation of a file to give to blast taxid and SEQ acc nr
taxid_assemblyaccnr_2_seqaccnr_taxid.pl ../taxid_lists/host_complete_genomes_taxid_accnr.tsv ../taxid_lists/host_complete_genomes_seqaccnr_taxid.tsv


# DB blast indexation using env blast-v2.12.0
pigz -d -p 8 -k -c *.fna.gz | makeblastdb -dbtype 'nucl' -input_type 'fasta' -title host_complete_genomes_db -parse_seqids -out host_complete_genomes_db/host_complete_genomes_db -blastdb_version '5' -logfile host_complete_genomes_db/host_complete_genomes_db_makblastdb_log.txt -taxid_map /media/data/ANSES/PrepMedVet_analyses/taxid_lists/host_complete_genomes_accnr_taxid_4makeblastdb.tsv
