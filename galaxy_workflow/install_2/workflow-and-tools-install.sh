workflow-to-tools -w Galaxy-Workflow-V1_BACT__Assembly___identification.ga  -o Galaxy-Workflow-V1_BACT__Assembly___identification.yml
workflow-to-tools -w Galaxy-Workflow-V1_VIRAL__Assembly___identification.ga -o Galaxy-Workflow-V1_VIRAL__Assembly___identification.yml
workflow-to-tools -w Galaxy-Workflow-V2__Host_caracterisation.ga            -o Galaxy-Workflow-V2__Host_caracterisation.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1_BACT__Assembly___identification.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1_VIRAL__Assembly___identification.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V2__Host_caracterisation.yml
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1_BACT__Assembly___identification.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1_VIRAL__Assembly___identification.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V2__Host_caracterisation.ga
