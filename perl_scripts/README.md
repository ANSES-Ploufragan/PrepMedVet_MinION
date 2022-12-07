perl scripts to deduce leaves taxids from a list of taxids obtained from taxid_lists/README.md :
- ```get_refseq_virus_completegenomes.pl``` is dedicated to virus/phages
- ```get_refseq_virus_completegenomes.pl``` is dedicated to bacteria/archae/fungi

They have no perl dependencies.

Bash script was not used because ncbi script ```get_species_taxids.sh``` to get leaves taxid run sh shell, interfering with bash loop and making the loop failing.
This interference is not encountered in perl.

The perl scripts ```get_refseq_*_completegenomes.pl``` needs that two conda environments (whose yaml files are in _envs_ directory) are installed before running:
- blast-v2.12.0.yaml (to use ```get_species_taxids.sh```)
- ncbi-genome-download-0.3.1.yaml (to download complet genomes specific to the list of taxids provided)
