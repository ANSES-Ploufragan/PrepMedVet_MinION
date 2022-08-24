Workflow Galaxy PrepMedVet

# Table of contents
1. [Log in and data loading] (#Log)
2. [V1: BIGONE] (#V1) 
3. [V2: BIGTWO] (#V2)
4. [V3] (#V3)

[[_TOC_]]

# Log in and data loading

## Log in

* Run Firefox web browser
* The default displayed web page will be the Galaxy interface (accessible by clicking on "home button" too)
* Click on __"Log in or register"__ ("Authentification et enregistrement"). Then:
  - type for:
      - user: pmv
      - password: PrepMedVet2023
  - validate
  
## Upload data for analyses

* At the top left-hand corner, click on __"Upload Data"__

### taxid files of pathogens or hosts

* To upload taxid (text) files:
  - select: __regular__
  - click on __"Choose local file"__
  - browse to ```/home/pmv/PrepMedVet_analyses/taxid_lists/```
  - select both files:
      - ```taxid_hosts```
      - ```taxid_pathogens```
  - click on __"Open"__ ("Ouvrir")
  - click on __"Start"__ ("Commencer")
  - click on __"Close"__ ("Fermer")
  - wait that the two files appear in __Green__ in the right column (your history)


### MinION reads

* To upload taxid (text) files:
  - select: __collection__
  - click on __"Choose local file"__
  - browse to:
      - ```/home/pmv/PrepMedVet_test/fastq_raw/[sample]/``` for test data or
	  - ```/var/lib/minknow/data/``` for real MinION reads freshly created by MinKNOW/guppy_gpu
	  
  - select the 20 first ```.fastq``` or ```.fastq.gz``` files (each file contains 4000 reads) for your first analysis
  - click on __"Open"__ ("Ouvrir")
  
  - click on __"Start"__ ("Commencer")
  - wait that the two files appear in __Green__ in the left column (your history)
  - click on __"Build"__
  - check the box "Hide original element" if not already (to have only one element in your history for all these 20 files) and fill the __Name__ (field) you want to give to this dataset,
  - click on __"Close"__ ("Fermer")
  - the dataset appears  in __Green__ in the right column (your history)

### Rename your history with a explicite name

- click on __"Unnamed"__ below "History" at the top right-hand corner
- type the new name, then click on the Enter touch of the keyboard.


### Find workflows to run analyses

* At the botton left-hand corner, click on __"All_workflows"__ (under "Workflow" section)
* You will find them bellow. Click on the one you want to use.


# V1: BIGONE

To use if there is no host in the sample.

This workflow search for viral and bacterial pathogens (for human or animals) and produce an alignement and an assembly of the detected pathogens.

All the steps are sub-workflows:
1. V1: Concatenate_reads_minion_files
2. V1: Megablast_virus_prok_from_reads
3. V1: Alignment + Variant calling
4. V1 VIRAL: Assembly + identification
5. V1 BACT: Assembly + identification

The workflow ```V1: BIGONE without read concatenation``` is the same but does not include the first step.

## V1: Concatenate_reads_minion_files

Concatenate the read files obtained from MinION sequencing: the user must have load them in his/her history.

## V1: Megablast_virus_prok_from_reads

1. The reads are cleaned and downsampled.
2. Reads are (megablast) aligned with the nt (local) databank.
3. The viral and bacterial pathogen references are identified.

## V1: Alignment + Variant calling

1. Alignment of reads with the identified viral or bacterial references (fasta).
2. We get the aligned reads.
3. Detection of SNPs.

## V1 VIRAL: Assembly + identification / V1 BACT: Assembly + identification

1. Assembly of previous reads.
2. Alignment (megablast) of the contigs with the nt (local) databank.


# V2: BIGTWO

To be used if one or several hosts are suspected in the sample.

The steps:
1. V1: Concatenate_reads_minion_files (see first previous sub-workflow)
2. V2: Host Identification
3. filtlong (reads cleaning)
4. V2: Alignment + Get unmapped reads
5. V1: BIGONE without read concatenation (see introduction to BIGONE)

## V2: Host Identification

1. The reads are cleaned and downsampled.
2. Reads are (megablast) aligned with the nt (local) databank.
3. The aligned references included in the hosts list (taxids) are extracted.

## V2: Alignment + Get unmapped reads

1. The reads are aligned with the identified host(s) reference(s).
2. We get unaligned reads.

# V3

To execute after the workflow V1 or V2.

The aim is the identification of unreferenced pathogens.

The steps:
1. V3 : concatenate megablast results if needed
2. V3 : alignment + assembly + megablast + tblastx

## V3 : concatenate megablast results if needed

**Must be executed ONLY if bacterial or viral species are identified after the assembly.**

Concatenation of megablast results.

## V3 : alignment + assembly + megablast + tblastx

1. We get all the references obtained in megablast (after assembly, see V1).
2. Alignment of the reads (not aligned with the host(s) if V2) with the references.
3. We get unaligned reads
4. Assembly of the unaligned reads
5. Alignment (megablast) of the contigs with the nt (local) databank
6. We get unidentified contigs
7. Alignment (tblastx) of the unidentified contigs with the nr (local) databank.



