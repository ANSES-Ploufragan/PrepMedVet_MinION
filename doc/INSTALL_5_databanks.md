- [Download and installation of needed databank](#download-and-installation-of-needed-databank)
  - [ref\_prok\_rep\_genomes](#ref_prok_rep_genomes)
  - [ref\_viruses\_rep\_genome](#ref_viruses_rep_genome)
  - [rvcg\_blast\_db and rbcg\_blast\_db](#rvcg_blast_db-and-rbcg_blast_db)
  - [nt and nr](#nt-and-nr)
  - [host\_complete\_genome\_db](#host_complete_genome_db)
- [Location of databank on an external USB-C plugged ssd](#location-of-databank-on-an-external-usb-c-plugged-ssd)



# Download and installation of needed databank

Databank to install and their purpose:
- rvcg_blast_db: ref/type complete genomes of virus/phages pathogens for first analyses
- rbcg_blast_db: ref/type complete genomes of bacteria/fungal/archae pathogens for first analyses
- nt: general search of small dataset, obtention of fasta references (for host(s) too)
- nr: general search for unidentified contigs

- host_complete_genome_db: complete genome assemblies for hosts (not found in ncbi nt, needed to remove host reads fastly)


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

## host_complete_genome_db

Go to directory: ```~/PrepMedVet_analyses/perl_scripts```

Run command:

```
mkdir /db/host_complete_genomes_db
./get_host_completegenomes.pl -o /db/host_complete_genomes_db/
```

# Location of databank on an external USB-C plugged ssd

* This can be done (read/write speed of almost 1 Gb/s) with caution:
  * read/write access to the complete path of the drive must be set so that Galaxy has the rights
  * disk can be automatically mounted at startup of the computer by adding to the __/etc/fstab__ file something like:
  ```
  UUID=083E035B2FD94834    /media/pmv/083E035B2FD94834  ntfs    uid=1000,gid=1000,umask=000,windows_names   0  0   
  ```
  > do a backup of your /etc/fstab file before any modification, to be able to recover the original

  - UUID can be obtained for the disk checking the listing returned by the command ```sudo blkdisk``` (unic identifier for the ssd/harddrive avoid changement of assignation observed sometime when using /dev/sdb5 for instance that can become /dev/sda5 at another boot)
  - uid of current user can be obtained with the command ```id -u username```
  - gid of current user can be obtained with the command ```id -g username```
  - umask is needed to let read/write access to all users
  - windows_names is for ntfs compatibilities