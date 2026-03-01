
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

There is significant coupling between annotation resources. As of 3.22, org.Hs.eg.db and GO.db
need to be synchronized to the same version of GO, even though the org
pack is based on annotations from NCBI, which notes (at the FTP site):

```
           This file reports the GO terms that have been associated
           with Genes in Entrez Gene.

           Gene ontology annotations are imported from external sources
           by processing the gene_association files on the GO ftp site: 
           http://www.geneontology.org/GO.current.annotations.shtml
           and comparing the DB_Object_ID to annotation in Gene,
           as also reported in gene_info.gz. This process is limited to the 
           species listed in go_process.xml file.

           For all other species, gene ontology terms are computed at the time
           of annotation by running InterProScan 
           (https://interproscan-docs.readthedocs.io/en/latest/), including analyses 
           against PANTHER trees on all annotated proteins and collating the 
           results by GeneID. These data are also provided in the GAF (GO 
           Annotation File) format in Genomes FTP. For example, see: 
           ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/949/774/975/GCF_949774975.1_mLagAlb1.1/
```
The shtml URL given above is defunct.  We are not told exactly how NCBI produces
its annotations, based on this README excerpt.

geneontology.org provides guidance on annotations [here](https://geneontology.org/docs/download-go-annotations/#1-commonly-studied-organisms).

For human, the download link is [here](https://current.geneontology.org/products/pages/downloads.html).
The header of `goa_human.gaf` indicates that it is based on the image of GO of 2025-10-05.

The collections of past releases at https://release.geneontology.org/ indicate one of 2025-10-10, but not 10-05.


