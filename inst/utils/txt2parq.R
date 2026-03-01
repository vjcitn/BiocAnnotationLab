txt2parq = function(stub="gene2refseq", pref="Hs") {
 x = data.table::fread(sprintf("%s.%s.gz", pref, stub))
 arrow::write_parquet(x, sprintf("%s.%s.parquet", pref, stub), compression="zstd", compression_level=10)
}
