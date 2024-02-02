# Description of perl / bash scripts

## cmd_create_blastdb.bash

* Creates __rvcg_blast_db__ viral pathogens databank

## cmd_creates_env.bash

* Creates conda environments:
  - blast-v2.12.0 and
  - ncbi-genome-download-0.3.1

## cmd_get_host_completegenomes.bash

* All commands to:
  - download host complete genomes sequences 
  - create __host_complete_genomes_db__
  - create files usefull for TAXID...pl scripts
  - create __../python_scripts/assemblyaccnr_seqaccnr/__ directory with files named [assemblyaccessionnumber].[version].txt and storing __sequence accession numbers__ really found in host_complete_genomes_db

## cmd_install_ncbi_db.pl

* perl script to download/install __nt__ and __nr__ databases

## cmd_install_pathogens_completegenomes_db.bash



## get_refseq_virus_completegenomes.pl

* perl scripts to deduce leaves taxids from a list of taxids obtained from taxid_lists/README.md file:
    - ```get_refseq_virus_completegenomes.pl``` is dedicated to virus/phages
    - ```get_refseq_virus_completegenomes.pl``` with option ```-b``` is dedicated to bacteria/archae/fungi
    > They have no perl dependencies.
    >
    > The perl scripts ```get_refseq_virus_completegenomes.pl``` needs that two conda environments (whose yaml files are in _envs_ directory) are installed before running:
    > - blast-v2.12.0.yaml (to use ```get_species_taxids.sh```)
    > - ncbi-genome-download-0.3.1.yaml (to download complet genomes specific to the list of taxids provided)
    >
    > A bash script was not used because ncbi script ```get_species_taxids.sh``` to get leaves taxid run sh shell, interfering with bash loop and making the loop failing.
    This interference is not encountered in perl.


## 
