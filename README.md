
# BiocAnnotationLab: A developmental coding and data laboratory for strategies used in Bioconductor to curate genomic annotation for genomic data science

## Motivation

Bioconductor's annotation resources are extensive and can be challenging to maintain
for various reasons.  This package collects information relevant to 

- reducing complexity of annotation management
- taking advantage of new approaches to data representation
- supporting "self-service" solutions for those needing rapid revision of annotation resources

Basic facts:

- `GO.db`
    - Package is downloaded by over 20000 distinct IPs per month
    - It is powered by a 70MB SQLite database with 14 tables following a bespoke schema
    - The production of the GO.db package is mixed with production of numerous other annotation
packages in the BioconductorAnnotationPipeline system.
    - A parquet-based representation with equivalent content can fit in 7MB of disk.  See
[GO.db3](https://github.com/vjcitn/GO.db3) and note the OBO-parquet transformation
resource at [BiocGOprep](https://github.com/vjcitn/BiocGOprep).
    - Yet another approach to Gene Ontology (and indeed all ontologies at OBOFoundry)
leverages semantic SQL -- see [ontoProc2](https://vjcitn.github.io/ontoProc2/), in development.

- `org.*.*.db`
    - All the org.*.eg.db are based on curation of resources from NCBI
    - These do not need to be carved up for different organisms; see the
[RNCBIgene](https://vjcitn.github.io/RNCBIGene/) package in development.
    - Project-specific resources like SGD, TAIR, PLASMO had special casing
in the pipeline, and this needs a fresh, maintainable approach

- `TxDb.*.*...`
    - The architect is still with the project
    - Tooling to move from SQLite to parquet is available and produces 7x reduction
in footprint
    - Upstream tasks are well-documented, but should be reviewed regularly
