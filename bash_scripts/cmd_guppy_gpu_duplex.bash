#!/bin/bash

# global var
barcode_kit='SQK-NBD112-96'
# flowcell='FLO-MIN106'
cfg_f='dna_r9.4.1_e8.1_hac.cfg' 
summary_f='sequencing_summary_FAT31176_0af3286d.txt'
records_per_fastq=4000
min_qscore=7
# sample_sheet="20220926-run_MinION_name_barcode.csv" # not working

# command for using summary_f
ech='barcode72' # done from 96 to ...

guppy_basecaller_duplex --input_path fast5_pass/$ech --save_path fastq_duplex/$ech -x "cuda:0" --config $cfg_f  --duplex_pairing_mode 'from_1d_summary' --duplex_pairing_file $summary_f -q $records_per_fastq --compress_fastq --min_qscore $min_qscore --detect_barcodes --detect_adapter --detect_primer --detect_mid_strand_barcodes --detect_mid_strand_adapter --trim_adapters --num_callers 1 --gpu_runners_per_device 1 --chunks_per_runner 320 --chunk_size 2000 --front_window_size 50 --rear_window_size 50 --barcode_kits $barcode_kit

# 1 x 320 x 2000 x 12600 = 14 000 000 000

# # command for using pairing_reads_f
# pairing_reads_f=''
# guppy_basecaller_duplex --input_path fastq_raw/$ech --save_path fastq_duplex/$ech -x "cuda:0" --config $cfg_f  --duplex_pairing_mode 'from_pair_list' --duplex_pairing_file $pairing_reads_f

# # options for RNA sequencing
# --reverse_sequence
# 	Reverse the called sequence (for RNA sequencing).
# --u_substitution
# 	Substitute 'U' for 'T' in the called sequence (for RNA sequencing).
