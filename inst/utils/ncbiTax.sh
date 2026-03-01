#!/bin/bash
#
# ncbiTax: args are taxid, 2 letter tag, NCBI 'stub' gene2[.*].gz
# uses R program txt2parq.R requiring data.table and arrow
# example: source ncbiTax.sh 9606 Hs gene2pubmed
# will produce Hs.gene2pubmed.parquet
#
TAXID=$1
TAG=$2
STUB=$3
zcat $STUB.gz | head -1 | gzip - > /tmp/head
zcat $STUB.gz | grep "^$TAXID	" | gzip - >  /tmp/Hs.$STUB.gz
cat /tmp/head /tmp/Hs.$STUB.gz > Hs.$STUB.gz
Rscript -e "source('txt2parq.R'); txt2parq('$STUB')"
