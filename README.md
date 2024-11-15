# Repository of PrepMedVet_MinION, part of [PrepMedVet ANR project](https://www.saps-paris-saclay.fr/actualites/Historique/projet-anr-franco-allemand-prepmedvet)

## Aim

The PrepMedVet ANR project is dedicated to the detection/identification in the field of pathogens.

In this project, the bioinformatics team of the Anses of Ploufragan implemented a global
solution to sequence samples using a [MinION sequencing device](https://nanoporetech.com/products/sequence/minion) (Nanopore) and to do the bioinformatics analyses of raw read __in the field__ on a dedicated strong laptop:
- processor: core i9, 
- graphic card: Nvidia RTX3080
- RAM: 64 GB
- nvme ssd with 2 TB for system
- external ssd with 2 TB for databanks

This repository contains:
- advices for installation in the __doc__ directory (system, drivers, cuda, nanopore MinKNOW and dorado GPU, galaxy, galaxy workflows)
- it contains files of an ansible Galaxy instance ran on the laptop (__galaxy__)
- it contains Galaxy workflows dedicated to sample analyses to find pathogens (__galaxy_workflow__)
- it contains perl and/or python scripts used respectively to get needed local databank from NCBI (mainly) or to be used in Galaxy workflows, respectively

NO GARANTY can be given because of the specificities of hardwares used in your own analyses if you use the workflows of this project

## Workflows summaries

> Note: big workflows can have subworkflows not listed here but present in this repository

* BIGONE: main part to detect/identify pathogen(s) in a sample (a pure one or an enriched one)
* BIGTWO: remove detected host reads, then search for pathogens in remaining data using BIGONE
* BIGTHREE: search for pathogens in unidentified contigs of BIGTWO results
* BIGFOUR: assemble unused reads in BIGTWO, then search for distant homologies in contigs obtained.

## Videos

* Soon available at: ...

## Citation

Soon available. If you use this work and publish, please cite this github repository:
https://github.com/ANSES-Ploufragan/PrepMedVet_MinION
