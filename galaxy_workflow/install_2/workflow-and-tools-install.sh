export ip=$1
export api=$2
workflow-to-tools -w Galaxy-Workflow-V1_BACT__Assembly___identification.ga  -o Galaxy-Workflow-V1_BACT__Assembly___identification.yml
workflow-to-tools -w Galaxy-Workflow-V1_VIRAL__Assembly___identification.ga -o Galaxy-Workflow-V1_VIRAL__Assembly___identification.yml
workflow-to-tools -w Galaxy-Workflow-V2__Host_caracterisation.ga            -o Galaxy-Workflow-V2__Host_caracterisation.yml
shed-tools install -g http://$ip  -a $api -t Galaxy-Workflow-V1_BACT__Assembly___identification.yml
shed-tools install -g http://$ip  -a $api -t Galaxy-Workflow-V1_VIRAL__Assembly___identification.yml
shed-tools install -g http://$ip  -a $api -t Galaxy-Workflow-V2__Host_caracterisation.yml
workflow-install  -g http://$ip  -a $api --publish_workflows -w Galaxy-Workflow-V1_BACT__Assembly___identification.ga
workflow-install  -g http://$ip  -a $api --publish_workflows -w Galaxy-Workflow-V1_VIRAL__Assembly___identification.ga
workflow-install  -g http://$ip  -a $api --publish_workflows -w Galaxy-Workflow-V2__Host_caracterisation.ga
