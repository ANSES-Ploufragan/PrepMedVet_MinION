#!/usr/bin/bash
conda env install -f /envs/blast-v2.12.0.yaml
conda env install -f /envs/ncbi-genome-download-0.3.1.yaml

$dbdir='/db/'
$virdb="${db_dir}rvcg_blast_db"
$bactdb="${db_dir}rbcg_blast_db"
sudo mkdir $virdb
sudo mkdir $bactdb
sudo chown pmv:galaxy $virdb
sudo chown pmv:galaxy $bactdb

perl -r ../taxid_lists/README.md -o $virdb -keep_taxid
perl -r ../taxid_lists/README.md -o $bactdb -keep_taxid -b

sudo chown -R galaxy:galaxy $virdb
sudo chown -R galaxy:galaxy $bactdb

# then need to add path "${virdb}rvcg_blast_db" to blast tool in Galaxy
# then need to add path "${bactdb}rbcg_blast_db" to blast tool in Galaxy
