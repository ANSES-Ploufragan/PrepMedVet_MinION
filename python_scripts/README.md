# Python script purpose and their conda env

[[TOC]]

## MEGABLAST_TAB_get_acc_under_taxid_in_out.py

* __not used currently__, except as command line tool (therefore __not in Galaxy__)
 
* conda env: MEGABLAST_TAB_get_acc_under_taxid_in_out.yaml

* aim: __Get accession numbers of megablast results in or out given taxonomic branchs__

    Original script to get:

    - all the __leave__ accession numbers (~species) of a blast tsv result file
      __included__ in the trees related to TAXID provided by user in a list
    - all the __leave__ accession numbers (~species) of a blast tsv result file
      __excluded__ of the trees related to TAXID provided by user in a list
      
* in:

* out:

> Note: This script has been splitted in 2 scripts to simplify conda env handling
and have one script by Galaxy task.

## MEGABLAST_TAB_get_taxid_acc.py

* conda env: MEGABLAST_TAB_get_taxid_acc.yaml

* aim: __Get taxid and accession numbers of a megablast result__

    Get all the __leave__ accession numbers (~species) of a blast tsv result file.

* in: megablast tabular file (25 columns, acc number in col 2)

* out: tabular file (tsv) with on each line: taxid accession_number

## MEGABLAST_TAB_select_acc_under_taxids.py

* conda env: MEGABLAST_TAB_select_acc_under_taxids.yaml

* aim: __Get accession numbers of megablast results in or out given taxonomic branchs__

    Get:

    - all the __leave__ accession numbers (~species) of a blast tsv result file
      __included__ in the trees related to TAXID provided by user in a list
    - all the __leave__ accession numbers (~species) of a blast tsv result file
      __excluded__ of the trees related to TAXID provided by user in a list
      
* in:
     
    - taxid file: list of __taxid to keep__ (can be inner tree taxids)
    - tabular file (__tsv__) of __taxids__ and related __accession_numbers__ (provided by __MEGABLAST_TAB_get_taxid_acc__)
    - [Optional] minimal number of reads matching an accession number to take it into account
    
* out:

    - txt file of accession numbers found __IN__ taxid ncbi taxonomy tree(s)
    - tabular file (tsv) of (leave) taxids and accession numbers found __IN__ taxid ncbi taxonomy tree(s)
    - txt file of accession numbers found __OUT__ taxid ncbi taxonomy tree(s)
    - tabular file (tsv) of (leave) taxids and accession numbers found __OUT__ taxid ncbi taxonomy tree(s)

> Note: before first use, need to be ran with two specific options to load ete3 databank: --load_ncbi_tax_f --ncbi_tax_f file_path_to_ete3_db

## TAXID_genusexpand_taxid2acc.py

* conda env: TAXID_genusexpand_taxid2acc.yaml

* aim: __find accession numbers of complete genomes related to provided taxids__ 

    Search accession number of complete genome of the species linked to taxid provided. Starts at species rank, goes upstream in taxonomy until order level if needed: stop when at less 1 ref accession of complete genome is found.

* in: tabular file (tsv) of (leave) taxids and accession numbers found __IN__ taxid ncbi taxonomy tree(s)

* out: txt file of accession numbers of __complete genomes__ of species 

> Note: before first use, need to be ran with two specific options to load ete3 databank : --load_ncbi_tax_f --ncbi_tax_f file_path_to_ete3_db


## TAXID_get_sp_taxid_from_taxid_list.py

* __not used currently__, except as command line tool (therefore __not in Galaxy__)

* conda env: TAXID_get_sp_taxid_from_taxid_list.yaml

* aim: __from a list of taxids (immer tree included), provde a list of leave taxids (~species)__

* in: txt file of __taxids__ (possibly inner taxids in taxonomic tree)

* out: txt file __leave taxids__ (~species) 

> Note: before first use, need to be ran with two specific options to load ete3 databank : --load_ncbi_tax_f --ncbi_tax_f file_path_to_ete3_db


## update_krona_database.py

* aim: __update krona and krona_accession database(s)__

* in:
        - db to update (krona, krona_accession)
        - directory to store this db

> Note: script of Pierrick? missing shebang