
# BiocAnnotationLab: A developmental coding and data laboratory for strategies used in Bioconductor to curate genomic annotation for genomic data science

## Motivation

Bioconductor's annotation resources are extensive and can be challenging to maintain
for various reasons.  This package collects information relevant to 

- reducing complexity of annotation management
- taking advantage of new approaches to data representation
- supporting "self-service" solutions for those needing rapid revision of annotation resources

See the vignette (Get started tab above) for more details.  There is a "next steps"
component.  Visitors are invited to comment in repository issues.

## Requirements

### Gene Ontology and Gene Ontology Annotation

NCBI uses Gene Ontology Consortium "Gene Annotation Format" (GAF) files
to produce its mapping.  We will work directly with GAF.

### Updating the user experience

Methods of the tidyverse and dplyr/dbplyr will be emphasized, to move
beyond the bespoke AnnotationDbi framework.
