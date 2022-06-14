Workflow Galaxy PrepMedVet

# Table of contents
1. [V1: BIGONE] (#V1) 
2. [V2: BIGTWO] (#V2)
3. [V3] (#V3)

# V1: BIGONE

Dans le cas où il n'y a pas d'hôte(s) dans l'échantillon.

Ce workflow recherche des pathogènes viraux et bactériens et produit un alignement
et un assemblage des pathogènes détectés.

Les étapes sont toutes des sous-workflows:
1. V1: Concatenate_reads_minion_files
2. V1: Megablast_virus_prok_from_reads
3. V1: Alignment + Variant calling
4. V1 VIRAL: Assembly + identification
5. V1 BACT: Assembly + identification

Le workflow ```V1: BIGONE without read concatenation``` est le même sans la première étape.

## V1: Concatenate_reads_minion_files

Concatène les fichiers de reads issus du séquençage MinION, l'utilisateur doit les avoir chargé dans l'historique.

## V1: Megablast_virus_prok_from_reads

1. Les reads sont nettoyés et sous-échantillonnés.
2. Un alignement des reads avec megablast sur nt (local) est fait.
3. Les références virales et bactériennes sont identifiées.

## V1: Alignment + Variant calling

1. Alignement des reads versus les références virales ou bactériennes identifiées.
2. Récupération des reads mappés.
3. Détection des SNPs.

## V1 VIRAL: Assembly + identification / V1 BACT: Assembly + identification

1. Assemblage des reads précédents.
2. Alignement des contigs versus nt avec megablast.


# V2: BIGTWO

Workflow a executer dans le cas où un hôte (ou plusieurs) est suspecté dans l'échantillon.

Les étapes:
1. V1: Concatenate_reads_minion_files (voir précédemment)
2. V2: Host Identification
3. filtlong (nettoyage des reads)
4. V2: Alignment + Get unmapped reads
5. V1: BIGONE without read concatenation (voir précédemment)

## V2: Host Identification

1. Les reads sont nettoyés et sous-échantillonnés.
2. Un alignement des reads avec megablast sur nt (local) est fait.
3. Les références matchant dans la liste des hôtes sont extraites.

## V2: Alignment + Get unmapped reads

1. Alignement des reads versus les références hôtes identifiées.
3. Récupération des reads non mappés.
3. Détection des SNPs.

# V3

A executer après le workflow V1 ou V2.

Le but est d'identifier des pathogènes non référencés.

Les étapes:
1. V3 : concatenate megablast results if needed
2. V3 : alignment + assembly + megablast + tblastx

## V3 : concatenate megablast results if needed

**A executer seulement si des espèces bactériennes et virales sont identifiées après l'assemblage.**

Concaténation des résulats de megablast.

## V3 : alignment + assembly + megablast + tblastx

1. Récupération de toutes les références de megablast (après assemblage, voir V1)
2. Alignement des reads (non alignés sur l'hôte si V2) versus les références.
3. Récupération des reads non mappés
4. Assemblage des reads
5. Alignement des contigs versus nt avec megablast
6. Récupération des contigs sans identification
7. Alignement des contigs sur nr avec tblastx



