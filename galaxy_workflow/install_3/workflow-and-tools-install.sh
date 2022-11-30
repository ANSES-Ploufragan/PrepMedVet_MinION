workflow-to-tools -w Galaxy-Workflow-V1__BIGONE.ga                            -o Galaxy-Workflow-V1__BIGONE.yml
workflow-to-tools -w Galaxy-Workflow-V1__BIGONE_without_read_concatenation.ga -o Galaxy-Workflow-V1__BIGONE_without_read_concatenation.yml
workflow-to-tools -w Galaxy-Workflow-V2__BIG_TWO.ga                           -o Galaxy-Workflow-V2__BIG_TWO.yml

shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1__BIGONE.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V1__BIGONE_without_read_concatenation.yml
shed-tools install -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb -t Galaxy-Workflow-V2__BIG_TWO.yml

workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1__BIGONE.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V1__BIGONE_without_read_concatenation.ga
workflow-install  -g http://192.168.101.87  -a 0356f1f8824d49d1c5815b14c976e9bb --publish_workflows -w Galaxy-Workflow-V2__BIG_TWO.ga
