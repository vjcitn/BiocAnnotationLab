#!/bin/bash
# Quick Start Guide for SQLite to Parquet Conversion
# This script demonstrates the complete workflow

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  SQLite to Parquet Converter - Quick Start Guide         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Install dependencies
echo "Step 1: Installing dependencies..."
pip install -q duckdb
echo "✓ DuckDB installed"
echo ""

# Step 2: Create test database
echo "Step 2: Creating test database..."
python create_test_db.py test_genome.db
echo ""

# Step 3: Convert to Parquet
echo "Step 3: Converting to Parquet..."
python sqlite_to_parquet.py test_genome.db parquet_output/ --compression zstd
echo ""

# Step 4: Show results
echo "Step 4: Results"
echo "Output files created:"
ls -lh parquet_output/*.parquet | awk '{printf "  %-25s %8s\n", $9, $5}'
echo ""

# Step 5: Verify data with DuckDB
echo "Step 5: Verifying data (sample query)..."
python3 << 'EOF'
import duckdb
con = duckdb.connect()

# Query the Parquet files directly
result = con.execute("""
    SELECT 
        tx_chrom as chromosome,
        tx_type as type,
        COUNT(*) as count
    FROM 'parquet_output/transcript.parquet'
    GROUP BY tx_chrom, tx_type
    ORDER BY tx_chrom, count DESC
    LIMIT 10
""").df()

print(result.to_string(index=False))
con.close()
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Conversion Complete!                                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  • View README.md for detailed usage examples"
echo "  • Query your Parquet files with DuckDB, Pandas, or Polars"
echo "  • Customize compression with --compression and --level options"
echo ""
