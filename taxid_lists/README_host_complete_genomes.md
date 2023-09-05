* host_complete_genomes_accnr.txt

> Complete list of accession numbers of __host complete genomes database__
  - deduced from fasta files of the db when it was created,
  - will be used by python script ```accnr2accnr_taxid.py``` to create other files listed here.

* host_complete_genomes_taxid_accnr.tsv

> List of taxids and accession numbers of the host complete genomes database. Created by ```accnr2accnr_taxid.py``` using esearch ncbi function (__needs network__)
WARN: when running python scripts, some taxids will be missing because of deletion in ncbi or network small failure: they must be __completed manually__

* host_complete_genomes_missing_accnr.txt

> List of accession numbers of the host complete genomes database missing in ncbi. Created by the python script ```accnr2accnr_taxid.py``` that write each acc nr in this file when there is failure to obtain its taxid. Will help to __complete manually__ taxids related to these accession numbers in host_complete_genomes_taxid_accnr.tsv file
