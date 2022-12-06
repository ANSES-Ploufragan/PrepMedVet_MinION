workflow-to-tools -w Galaxy-Workflow-Catch_clean_gi_to_DL_ref.ga                        -o Galaxy-Workflow-Catch_clean_gi_to_DL_ref.yml
workflow-to-tools -w Galaxy-Workflow-V1__Alignment___Variant_calling.ga                 -o Galaxy-Workflow-V1__Alignment___Variant_calling.yml
workflow-to-tools -w Galaxy-Workflow-V1__Concatenate_reads_minion_files.ga              -o Galaxy-Workflow-V1__Concatenate_reads_minion_files.yml
workflow-to-tools -w Galaxy-Workflow-V1__Megablast_virus_prok_from_reads.ga             -o Galaxy-Workflow-V1__Megablast_virus_prok_from_reads.yml
workflow-to-tools -w Galaxy-Workflow-V2__Alignment___Get_unmapped_reads.ga              -o Galaxy-Workflow-V2__Alignment___Get_unmapped_reads.yml
workflow-to-tools -w Galaxy-Workflow-V3___alignment___assembly___megablast___tblastx.ga -o Galaxy-Workflow-V3___alignment___assembly___megablast___tblastx.yml
workflow-to-tools -w Galaxy-Workflow-V3___concatenate_megablast_results_if_needed.ga    -o Galaxy-Workflow-V3___concatenate_megablast_results_if_needed.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-Catch_clean_gi_to_DL_ref.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1__Alignment___Variant_calling.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1__Concatenate_reads_minion_files.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1__Megablast_virus_prok_from_reads.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V2__Alignment___Get_unmapped_reads.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V3___alignment___assembly___megablast___tblastx.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V3___concatenate_megablast_results_if_needed.yml
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-Catch_clean_gi_to_DL_ref.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1__Alignment___Variant_calling.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1__Concatenate_reads_minion_files.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1__Megablast_virus_prok_from_reads.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V2__Alignment___Get_unmapped_reads.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V3___alignment___assembly___megablast___tblastx.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V3___concatenate_megablast_results_if_needed.ga
