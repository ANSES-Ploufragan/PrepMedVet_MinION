# Download and installation of needed databank

Databank to install and their purpose:
- rvcg_blast_db: ref/type complete genomes of virus/phages pathogens for first analyses
- rbcg_blast_db: ref/type complete genomes of bacteria/fungal/archae pathogens for first analyses
- nt: general search of small dataset, obtention of fasta references (for host(s) too)
- nr: general search for unidentified contigs


## ref_prok_rep_genomes

## ref_viruses_rep_genome

## rvcg_blast_db and rbcg_blast_db

__rvcg_blast_db__ databank is for first search of virus/phages pathogens and contains all ref/type complete genomes of pathogens (results prefered to more general approach so as to privilegiate complete genomes in results).
__rbcg_blast_db__ databank is for first search of bacteria/fungi/archea pathogens and contains all ref/type complete genomes of pathogens (results prefered to more general approach so as to privilegiate complete genomes in results).

Go to directory: ```~/PrepMedVet_analyses/perl_scripts```

Run command:

```
./cmd_install_pathogens_completegenomes_db.bash
```

## nt and nr


Go to directory: ```~/PrepMedVet_analyses/perl_scripts```

Run command:

```
./cmd_install_ncbi_db.pl
```
