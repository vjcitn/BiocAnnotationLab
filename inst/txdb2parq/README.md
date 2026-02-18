# SQLite to Parquet Converter

A high-performance tool for converting SQLite databases to Parquet format using DuckDB's efficient zero-copy export capabilities. Optimized for genomic annotation databases and other large datasets.

## Features

- ⚡ **Fast**: Uses DuckDB's zero-copy export (no Python overhead)
- 🗜️ **Flexible compression**: Supports snappy, gzip, zstd, lz4, or uncompressed
- 📊 **Progress tracking**: Detailed logging of conversion progress
- 🎯 **Selective conversion**: Convert specific tables or all tables
- ✅ **Production-ready**: Comprehensive error handling and validation
- 📦 **Minimal dependencies**: Only requires DuckDB

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install DuckDB directly
pip install duckdb
```

## Quick Start

```bash
# Convert all tables with default settings (zstd compression)
python sqlite_to_parquet.py genome.db output_parquet/

# Convert specific tables only
python sqlite_to_parquet.py genome.db output_parquet/ --tables transcript exon

# Use maximum compression
python sqlite_to_parquet.py genome.db output_parquet/ --compression zstd --level 9

# Use fast compression
python sqlite_to_parquet.py genome.db output_parquet/ --compression snappy
```

## Usage

```
usage: sqlite_to_parquet.py [-h] [--tables TABLE [TABLE ...]]
                            [--compression {uncompressed,snappy,gzip,zstd,lz4}]
                            [--level N] [--row-group-size N] [--overwrite]
                            [--quiet] [--verbose]
                            sqlite_db output_dir

Convert SQLite database tables to Parquet format using DuckDB

positional arguments:
  sqlite_db             Path to SQLite database file
  output_dir            Output directory for Parquet files

optional arguments:
  -h, --help            show this help message and exit
  --tables TABLE [TABLE ...]
                        Specific table names to convert (default: all tables)
  --compression {uncompressed,snappy,gzip,zstd,lz4}
                        Compression codec (default: zstd)
  --level N             Compression level (codec-dependent, e.g., 1-9 for zstd)
  --row-group-size N    Rows per row group (default: 122880)
  --overwrite           Overwrite existing Parquet files
  --quiet               Suppress informational output
  --verbose             Enable verbose output
```

## Examples

### Basic Usage

```bash
# Convert entire database
python sqlite_to_parquet.py annotations.db parquet_output/
```

Output:
```
2024-02-18 10:30:15 - INFO - Output directory: /path/to/parquet_output
2024-02-18 10:30:15 - INFO - Starting conversion from: annotations.db
2024-02-18 10:30:15 - INFO - Compression: zstd
2024-02-18 10:30:15 - INFO - Attaching SQLite database...
2024-02-18 10:30:15 - INFO - Found 7 tables: cds, chrominfo, exon, gene, metadata, splicing, transcript
2024-02-18 10:30:15 - INFO - Converting table: cds
2024-02-18 10:30:15 - INFO -   Rows: 250,000, Columns: 6
2024-02-18 10:30:16 - INFO -   ✓ Completed: cds.parquet (8.45 MB)
...
```

### Convert Specific Tables

```bash
# Only convert the main annotation tables
python sqlite_to_parquet.py genome.db output/ \
  --tables chrominfo transcript exon gene
```

### Compression Options

```bash
# Maximum compression (slower, smallest files)
python sqlite_to_parquet.py genome.db output/ \
  --compression zstd --level 9

# Fast compression (faster, larger files)
python sqlite_to_parquet.py genome.db output/ \
  --compression snappy

# No compression (fastest, largest files)
python sqlite_to_parquet.py genome.db output/ \
  --compression uncompressed

# Balanced (recommended for most cases)
python sqlite_to_parquet.py genome.db output/ \
  --compression zstd --level 6
```

### Advanced Options

```bash
# Custom row group size for better parallelization
python sqlite_to_parquet.py genome.db output/ \
  --row-group-size 250000

# Overwrite existing files
python sqlite_to_parquet.py genome.db output/ --overwrite

# Quiet mode (only errors/warnings)
python sqlite_to_parquet.py genome.db output/ --quiet

# Verbose mode (detailed logging)
python sqlite_to_parquet.py genome.db output/ --verbose
```

## Compression Comparison

| Codec        | Speed    | Compression | Use Case |
|--------------|----------|-------------|----------|
| uncompressed | Fastest  | 1x          | Testing, temporary files |
| snappy       | Fast     | ~2-3x       | Good default, fast queries |
| lz4          | Fast     | ~2-3x       | Alternative to snappy |
| zstd         | Medium   | ~3-5x       | **Recommended** - best balance |
| gzip         | Slow     | ~4-6x       | Maximum compression needed |

### Recommendations

- **For genomic data**: `--compression zstd --level 6`
- **For fast queries**: `--compression snappy`
- **For storage optimization**: `--compression zstd --level 9`
- **For testing**: `--compression uncompressed`

## Performance Tips

1. **Row Group Size**: 
   - Default (122,880) works well for most cases
   - Increase (e.g., 500,000) for large tables with parallel queries
   - Decrease (e.g., 50,000) for many small queries

2. **Compression Level**:
   - zstd levels 1-3: Fast, good compression
   - zstd levels 4-6: Balanced (recommended)
   - zstd levels 7-9: Maximum compression, slower

3. **Memory**:
   - DuckDB handles memory efficiently
   - No special configuration needed for large databases

## Output Structure

The script creates one Parquet file per table:

```
output_parquet/
├── chrominfo.parquet
├── transcript.parquet
├── exon.parquet
├── cds.parquet
├── splicing.parquet
├── gene.parquet
└── metadata.parquet
```

## Reading Parquet Files

### Using Pandas

```python
import pandas as pd

# Read single table
df = pd.read_parquet('output_parquet/transcript.parquet')

# Read with column selection
df = pd.read_parquet('output_parquet/transcript.parquet', 
                     columns=['tx_name', 'tx_chrom', 'tx_start', 'tx_end'])

# Read with row filtering (predicate pushdown)
df = pd.read_parquet('output_parquet/transcript.parquet',
                     filters=[('tx_chrom', '==', 'chr1')])
```

### Using DuckDB

```python
import duckdb

con = duckdb.connect()

# Query directly without loading into memory
result = con.execute("""
    SELECT tx_chrom, COUNT(*) as transcript_count
    FROM 'output_parquet/transcript.parquet'
    GROUP BY tx_chrom
    ORDER BY transcript_count DESC
""").df()

print(result)
```

### Using Polars

```python
import polars as pl

# Read single table
df = pl.read_parquet('output_parquet/transcript.parquet')

# Lazy reading with filtering
df = (pl.scan_parquet('output_parquet/transcript.parquet')
        .filter(pl.col('tx_chrom') == 'chr1')
        .select(['tx_name', 'tx_start', 'tx_end'])
        .collect())
```

## Troubleshooting

### "Database is locked"
SQLite database is being accessed by another process. Close other connections or copy the database file.

### "Permission denied"
Ensure you have write permissions to the output directory:
```bash
mkdir -p output_parquet
chmod 755 output_parquet
```

### Large Memory Usage
DuckDB is generally memory-efficient, but for extremely large tables you can:
1. Convert tables individually: `--tables table_name`
2. Process in batches
3. Use lower compression levels

## Schema Information

For the genomic annotation schema described, the converted Parquet files will maintain:
- All data types (INTEGER, TEXT)
- Column names and order
- NULL values
- Row order (unless otherwise specified)

Foreign key relationships are preserved as values but not as constraints (Parquet doesn't support FK constraints).

## License

This script is provided as-is for converting SQLite databases to Parquet format.

## Requirements

- Python 3.7+
- DuckDB 0.9.0+

## Contributing

Suggestions and improvements welcome!
