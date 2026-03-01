#!/bin/bash
#
# ncbiTax: args are taxid, 2 letter tag, NCBI 'stub' gene2[.*].gz
# uses R program txt2parq.R requiring data.table and arrow
# example: ./ncbiTax.sh 9606 Hs gene2pubmed
# will produce Hs.gene2pubmed.parquet
#
TAXID=$1
TAG=$2
STUB=$3
echo "$STUB"

zcat "$STUB.gz" | head -1 | gzip - > /tmp/head

if [ "$STUB" = "gene_refseq_uniprotkb_collab" ]; then
  echo "Using column 3 for taxid filtering (uniprotkb format)"
  zcat "$STUB.gz" | awk -F'\t' -v taxid="$TAXID" '$3 == taxid' | gzip - > /tmp/$TAG.$STUB.gz
else
  zcat "$STUB.gz" | awk -F'\t' -v taxid="$TAXID" '$1 == taxid' | gzip - > /tmp/$TAG.$STUB.gz
fi
cat /tmp/head /tmp/$TAG.$STUB.gz > $TAG.$STUB.gz
Rscript -e "source('txt2parq.R'); txt2parq('$STUB', pref='$TAG')"
