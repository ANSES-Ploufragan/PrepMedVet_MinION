export ip=$1
export api=$2
workflow-to-tools -w Galaxy-Workflow-V1__BIGONE.ga                            -o Galaxy-Workflow-V1__BIGONE.yml
workflow-to-tools -w Galaxy-Workflow-V1__BIGONE_without_read_concatenation.ga -o Galaxy-Workflow-V1__BIGONE_without_read_concatenation.yml
workflow-to-tools -w Galaxy-Workflow-V2__BIG_TWO.ga                           -o Galaxy-Workflow-V2__BIG_TWO.yml

shed-tools install -g http://$ip  -a $api -t Galaxy-Workflow-V1__BIGONE.yml
shed-tools install -g http://$ip  -a $api -t Galaxy-Workflow-V1__BIGONE_without_read_concatenation.yml
shed-tools install -g http://$ip  -a $api -t Galaxy-Workflow-V2__BIG_TWO.yml

workflow-install  -g http://$ip  -a $api --publish_workflows -w Galaxy-Workflow-V1__BIGONE.ga
workflow-install  -g http://$ip  -a $api --publish_workflows -w Galaxy-Workflow-V1__BIGONE_without_read_concatenation.ga
workflow-install  -g http://$ip  -a $api --publish_workflows -w Galaxy-Workflow-V2__BIG_TWO.ga
