<div id="main" class="col-md-9" role="main">

# BiocAnnotationLab: developing new approaches to genomic annotation curation

<div class="section level2">

## Motivation

Bioconductor’s annotation resources are extensive and can be challenging
to maintain for various reasons. This package collects information
relevant to

-   reducing complexity of annotation management
-   taking advantage of new approaches to data representation
-   supporting “self-service” solutions for those needing rapid revision
    of annotation resources

Basic facts:

-   `GO.db`
    -   Package is downloaded by over 20000 distinct IPs per month
    -   It is powered by a 70MB SQLite database with 14 tables following
        a bespoke schema
    -   The production of the GO.db package is mixed with production of
        numerous other annotation packages in the
        BioconductorAnnotationPipeline system.
    -   A parquet-based representation with equivalent content can fit
        in 7MB of disk. See [GO.db3](https://github.com/vjcitn/GO.db3)
        and note the OBO-parquet transformation resource at
        [BiocGOprep](https://github.com/vjcitn/BiocGOprep).
    -   Yet another approach to Gene Ontology (and indeed all ontologies
        at OBOFoundry) leverages semantic SQL – see
        [ontoProc2](https://vjcitn.github.io/ontoProc2/), in
        development.
-   `org.*.*.db`
    -   All the org.\*.eg.db are based on curation of resources from
        NCBI
    -   These do not need to be carved up for different organisms; see
        the [RNCBIgene](https://vjcitn.github.io/RNCBIGene/) package in
        development.
    -   Project-specific resources like SGD, TAIR, PLASMO had special
        casing in the pipeline, and this needs a fresh, maintainable
        approach
-   `TxDb.*.*...`
    -   The architect is still with the project
    -   Tooling to move from SQLite to parquet is available and produces
        7x reduction in footprint
    -   Upstream tasks are well-documented, but should be reviewed
        regularly

</div>

<div class="section level2">

## Gene Ontology: approaches to curation

<div class="section level3">

### GO.db

Based on download counts, GO.db is a very popular resource in
Bioconductor. Here’s a basic use case, taken from the sources of goana.R
in limma.

    TERM <- suppressMessages(AnnotationDbi::select(GO.db::GO.db,keys=GOID,columns="TERM"))

Try it out:

<div id="cb2" class="sourceCode">

``` r
GOID = c("GO:0001960", "GO:0001961", "GO:0010803", "GO:0060334", "GO:0060338", 
"GO:0070099", "GO:0070103", "GO:0070107", "GO:0070758", "GO:1900234", 
"GO:1902205", "GO:1902211", "GO:1902214", "GO:1902226", "GO:1903881", 
"GO:2000446", "GO:2000492", "GO:2000659")
library(GO.db)
TERM <- suppressMessages(AnnotationDbi::select(GO.db::GO.db,keys=GOID,columns="TERM"))
head(TERM)
```

</div>

    ##         GOID                                                           TERM
    ## 1 GO:0001960     negative regulation of cytokine-mediated signaling pathway
    ## 2 GO:0001961     positive regulation of cytokine-mediated signaling pathway
    ## 3 GO:0010803 regulation of tumor necrosis factor-mediated signaling pathway
    ## 4 GO:0060334    regulation of type II interferon-mediated signaling pathway
    ## 5 GO:0060338     regulation of type I interferon-mediated signaling pathway
    ## 6 GO:0070099             regulation of chemokine-mediated signaling pathway

GO.db is self-descriptive.

<div id="cb4" class="sourceCode">

``` r
GO.db
```

</div>

    ## GODb object:
    ## | GOSOURCENAME: Gene Ontology
    ## | GOSOURCEURL: http://current.geneontology.org/ontology/go-basic.obo
    ## | GOSOURCEDATE: 2025-07-22
    ## | Db type: GODb
    ## | package: AnnotationDbi
    ## | DBSCHEMA: GO_DB
    ## | GOEGSOURCEDATE: 2025-Sep24
    ## | GOEGSOURCENAME: Entrez Gene
    ## | GOEGSOURCEURL: ftp://ftp.ncbi.nlm.nih.gov/gene/DATA
    ## | DBSCHEMAVERSION: 2.1

    ## 
    ## Please see: help('select') for usage information

We can learn about the underlying database.

<div id="cb7" class="sourceCode">

``` r
file.size(slot(GO_dbconn(), "dbname"))
```

</div>

    ## [1] 73560064

<div id="cb9" class="sourceCode">

``` r
DBI::dbListTables(GO_dbconn())
```

</div>

    ##  [1] "go_bp_offspring" "go_bp_parents"   "go_cc_offspring" "go_cc_parents"  
    ##  [5] "go_mf_offspring" "go_mf_parents"   "go_obsolete"     "go_ontology"    
    ##  [9] "go_synonym"      "go_term"         "map_counts"      "map_metadata"   
    ## [13] "metadata"        "sqlite_stat1"

GO.db presents environments with traversals of the ontological
hierarchy.

<div id="cb11" class="sourceCode">

``` r
get("GO:0001959", GO.db::GOBPCHILDREN)
```

</div>

    ##          isa          isa          isa          isa          isa          isa 
    ## "GO:0001960" "GO:0001961" "GO:0010803" "GO:0060334" "GO:0060338" "GO:0070099" 
    ##          isa          isa          isa          isa          isa          isa 
    ## "GO:0070103" "GO:0070107" "GO:0070758" "GO:1900234" "GO:1902205" "GO:1902211" 
    ##          isa          isa          isa          isa          isa          isa 
    ## "GO:1902214" "GO:1902226" "GO:1903881" "GO:2000446" "GO:2000492" "GO:2000659"

</div>

<div class="section level3">

### GO.db3: a parquet-based approach

In pursuit of a proof of concept, packages GO.db2 (SQLite-based) and
GO.db3 have been produced. GO.db2 uses a simplified schema for the
tables; GO.db3 uses parquet representations of GO.db’s tables.

To avoid conflict with dplyr’s `select`, GO.db3 defines `select3` to
emulate AnnotationDbi::select.

<div id="cb13" class="sourceCode">

``` r
library(GO.db3)
chk = select3("GO.db3",keys=GOID, columns=c("GOID", "TERM"), keytype="GOID")
head(chk)
```

</div>

    ##         GOID                                                           TERM
    ## 1 GO:0001960     negative regulation of cytokine-mediated signaling pathway
    ## 2 GO:0001961     positive regulation of cytokine-mediated signaling pathway
    ## 3 GO:0010803 regulation of tumor necrosis factor-mediated signaling pathway
    ## 4 GO:0060334    regulation of type II interferon-mediated signaling pathway
    ## 5 GO:0060338     regulation of type I interferon-mediated signaling pathway
    ## 6 GO:0070099             regulation of chemokine-mediated signaling pathway

We can learn about the underlying resources, in `extdata/go323` and
observe a sharp reduction in size of data footprint.

<div id="cb15" class="sourceCode">

``` r
pfns = dir(system.file("extdata", "go323", package="GO.db3"), full=TRUE)
head(basename(pfns))
```

</div>

    ## [1] "go_bp_offspring.parquet" "go_bp_parents.parquet"  
    ## [3] "go_cc_offspring.parquet" "go_cc_parents.parquet"  
    ## [5] "go_mf_offspring.parquet" "go_mf_parents.parquet"

<div id="cb17" class="sourceCode">

``` r
sum(file.size(pfns))
```

</div>

    ## [1] 7329583

We wrap the hierarchy-oriented environments in functions for now. The
environments are computed “on the fly”; only a few have been produced.

<div id="cb19" class="sourceCode">

``` r
get("GO:0001960", GO.db3::GOBPPARENTS())
```

</div>

    ##                 is_a                 is_a                 is_a 
    ##         "GO:0001959"         "GO:0009968"         "GO:0060761" 
    ## negatively_regulates 
    ##         "GO:0019221"

</div>

<div class="section level3">

### ontoProc2 for GO: using Semantic SQL

The [INCAtools semantic SQL](https://github.com/INCATools/semantic-sql)
project converts ontologies in OWL or OBO formats to SQLite. The README
remarks that

    SQLite provides many advantages
     - files can be downloaded and subsequently queried without network latency
     - compared to querying a static rdf, owl, or obo file, there is no startup/parse delay
     - robust and performant
     - excellent support in many languages
    Although the focus is on SQLite, this library can also be used for other 
    DBMSs like PostgreSQL, MySQL, Oracle, etc

Here’s how we can use a Semantic SQL representation of GO with
ontoProc2. The `GOID` vector was defined above.

<div id="cb22" class="sourceCode">

``` r
library(ontoProc2)
gosem = retrieve_semsql_conn("go")
chk1 = dplyr::tbl(gosem, "statements") |> 
  dplyr::filter(subject %in% GOID, predicate=="rdfs:label") |> 
  dplyr::select(subject, value)
head(chk1)
```

</div>

    ## # Source:   SQL [?? x 2]
    ## # Database: sqlite 3.51.2 [/Users/vincentcarey/Library/Caches/org.R-project.R/R/BiocFileCache/40e293b372b_go.db]
    ##   subject    value                                                         
    ##   <chr>      <chr>                                                         
    ## 1 GO:0001960 negative regulation of cytokine-mediated signaling pathway    
    ## 2 GO:0001961 positive regulation of cytokine-mediated signaling pathway    
    ## 3 GO:0010803 regulation of tumor necrosis factor-mediated signaling pathway
    ## 4 GO:0060334 regulation of type II interferon-mediated signaling pathway   
    ## 5 GO:0060338 regulation of type I interferon-mediated signaling pathway    
    ## 6 GO:0070099 regulation of chemokine-mediated signaling pathway

Note that the full representation of all facts and relationships in GO
entails a large footprint.

<div id="cb24" class="sourceCode">

``` r
file.size(slot(gosem, "dbname"))
```

</div>

    ## [1] 1694437376

</div>

<div class="section level3">

### Upshots

-   AnnotationDbi’s production of GO.db involves a complex pipeline with
    processes intermingled to address multiple objectives.
-   AnnotationDbi’s “select” method is in conceptual conflict with the
    widely used select method of dplyr.
-   [GO.db3](https://github.com/vjcitn/GO.db3?tab=readme-ov-file#godb3-is-an-experimental-package-that-partially-emulates-godb)
    is a near-complete functionally compatible replacement for GO.db.
-   Production of GO.db3 is independent of all other annotation
    production processes; parquet production from OBO is documented in
    [BiocGOprep](https://github.com/vjcitn/BiocGOprep).
-   `GO.db3::select3` is provided to emulate `AnnotationDbi::select`,
    but other interrogation interfaces based on the parquet
    representation should be devised. BiocGOprep produces parquet files
    following GO.db’s schema; this is not essential but was adopted to
    simplify producing compatibility with legacy approaches.
-   Both GO.db and GO.db3 present only a very limited view of the
    relationships encoded in Gene Ontology; a complete view is made
    available for SQL-based interrogation via ontoProc2.
-   ontoProc2 helps provide full programmatic access to any ontology
    managed in the Semantic SQL project.
-   It will be useful to work out exercises based on
    [rols](https://bioconductor.org/packages/rols), to help understand
    the added value of specific curation through packaging.

</div>

</div>

<div class="section level2">

## `org.*.eg.db`: curating NCBI gene-oriented annotation

The org packages are built using a complex pipeline that has a number of
shortcomings. We have examined its use of NCBI’s gene-oriented
annotation and propose a different approach.

See
[RNCBIGene](https://vjcitn.github.io/RNCBIGene/articles/RNCBIGene.html)
which is in development. Briefly, it is possible to

-   create parquet representations of all gzipped text at NCBI’s ftp
    site,
-   lodge these in egress-free cloud storage so that remote queries are
    supported,
-   provide retrieval and caching support to support efficient local
    usage,
-   avoid favoring any model organism for curated annotation support in
    Bioconductor.

</div>

<div class="section level2">

## Next steps

-   Community members are invited to comment on implications of
    strategic choices on annotation curation for their work.
-   GO.db3 should be brought to verifiable functional equivalence with
    GO.db.
-   RNCBIGene should be enhanced to emulate those `org.*.db` functions
    that are in use in the ecosystem.
-   Other annotation elements should be looked at for opporunities to
    use more efficient representations and interfaces.
-   It is of interest to note that there are no “first-class”
    representations of EFO or CL in Bioconductor. ontoProc2 and ontoProc
    address these ontologies, but are these sufficient?

</div>

<div class="section level2">

## Session information

<div id="cb26" class="sourceCode">

``` r
sessionInfo()
```

</div>

    ## R version 4.5.2 (2025-10-31)
    ## Platform: aarch64-apple-darwin20
    ## Running under: macOS Sequoia 15.7.3
    ## 
    ## Matrix products: default
    ## BLAS:   /System/Library/Frameworks/Accelerate.framework/Versions/A/Frameworks/vecLib.framework/Versions/A/libBLAS.dylib 
    ## LAPACK: /Library/Frameworks/R.framework/Versions/4.5-arm64/Resources/lib/libRlapack.dylib;  LAPACK version 3.12.1
    ## 
    ## locale:
    ## [1] en_US.UTF-8/en_US.UTF-8/en_US.UTF-8/C/en_US.UTF-8/en_US.UTF-8
    ## 
    ## time zone: America/New_York
    ## tzcode source: internal
    ## 
    ## attached base packages:
    ## [1] stats4    stats     graphics  grDevices utils     datasets  methods  
    ## [8] base     
    ## 
    ## other attached packages:
    ##  [1] ontoProc2_0.0.6      GO.db3_0.0.1         arrow_22.0.0.1      
    ##  [4] dplyr_1.2.0          GO.db_3.22.0         AnnotationDbi_1.72.0
    ##  [7] IRanges_2.44.0       S4Vectors_0.48.0     Biobase_2.70.0      
    ## [10] BiocGenerics_0.56.0  generics_0.1.4       BiocStyle_2.38.0    
    ## 
    ## loaded via a namespace (and not attached):
    ##  [1] KEGGREST_1.50.0     xfun_0.56           bslib_0.10.0       
    ##  [4] httr2_1.2.2         htmlwidgets_1.6.4   ontologyPlot_1.7   
    ##  [7] vctrs_0.7.1         tools_4.5.2         curl_7.0.0         
    ## [10] tibble_3.3.1        RSQLite_2.4.6       blob_1.3.0         
    ## [13] R.oo_1.27.1         pkgconfig_2.0.3     dbplyr_2.5.1       
    ## [16] desc_1.4.3          graph_1.88.1        assertthat_0.2.1   
    ## [19] lifecycle_1.0.5     compiler_4.5.2      textshaping_1.0.4  
    ## [22] Biostrings_2.78.0   Seqinfo_1.0.0       htmltools_0.5.9    
    ## [25] sass_0.4.10         yaml_2.3.12         pkgdown_2.2.0      
    ## [28] pillar_1.11.1       crayon_1.5.3        jquerylib_0.1.4    
    ## [31] R.utils_2.13.0      cachem_1.1.0        tidyselect_1.2.1   
    ## [34] digest_0.6.39       purrr_1.2.1         bookdown_0.46      
    ## [37] paintmap_1.0        grid_4.5.2          fastmap_1.2.0      
    ## [40] cli_3.6.5           magrittr_2.0.4      utf8_1.2.6         
    ## [43] withr_3.0.2         filelock_1.0.3      rappdirs_0.3.4     
    ## [46] bit64_4.6.0-1       rmarkdown_2.30      XVector_0.50.0     
    ## [49] httr_1.4.7          bit_4.6.0           otel_0.2.0         
    ## [52] R.methodsS3_1.8.2   ragg_1.5.0          png_0.1-8          
    ## [55] memoise_2.0.1       evaluate_1.0.5      knitr_1.51         
    ## [58] BiocFileCache_3.0.0 rlang_1.1.7         ontologyIndex_2.12 
    ## [61] glue_1.8.0          DBI_1.2.3           Rgraphviz_2.55.001 
    ## [64] BiocManager_1.30.27 jsonlite_2.0.0      R6_2.6.1           
    ## [67] systemfonts_1.3.1   fs_1.6.6

</div>

</div>
