# https://cran.r-project.org/web/packages/taxonomizr/readme/README.html

library(taxonomizr)
#note this will require a lot of hard drive space, bandwidth and time to process all the data from NCBI
prepareDatabase('accessionTaxa.sql')
blastAccessions<-c("Z17430.1","Z17429.1","X62402.1") 
ids<-accessionToTaxa(blastAccessions,'accessionTaxa.sql')
getTaxonomy(ids,'accessionTaxa.sql')