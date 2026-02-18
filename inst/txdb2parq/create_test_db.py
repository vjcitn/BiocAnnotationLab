#!/usr/bin/env python3
"""
Create a sample genomic annotation database for testing the SQLite to Parquet converter.

This script generates a small SQLite database with the schema provided,
populated with realistic test data.

Usage:
    python create_test_db.py [output_db_name.db]
"""

import sqlite3
import random
import sys
from pathlib import Path


def create_sample_database(db_path: str, num_chroms: int = 5, 
                          num_genes: int = 100, num_transcripts_per_gene: int = 2):
    """
    Create a sample genomic annotation database.
    
    Args:
        db_path: Output database file path
        num_chroms: Number of chromosomes to create
        num_genes: Number of genes to create
        num_transcripts_per_gene: Average number of transcripts per gene
    """
    print(f"Creating sample database: {db_path}")
    
    # Remove existing database if present
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create schema
    print("Creating schema...")
    
    cursor.execute("""
        CREATE TABLE chrominfo (
           _chrom_id INTEGER PRIMARY KEY,
           chrom TEXT UNIQUE NOT NULL,
           length INTEGER NULL,
           is_circular INTEGER NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE transcript (
           _tx_id INTEGER PRIMARY KEY,
           tx_name TEXT NULL,
           tx_type TEXT NULL,
           tx_chrom TEXT NOT NULL,
           tx_strand TEXT NOT NULL,
           tx_start INTEGER NOT NULL,
           tx_end INTEGER NOT NULL,
           FOREIGN KEY (tx_chrom) REFERENCES chrominfo (chrom)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE exon (
           _exon_id INTEGER PRIMARY KEY,
           exon_name TEXT NULL,
           exon_chrom TEXT NOT NULL,
           exon_strand TEXT NOT NULL,
           exon_start INTEGER NOT NULL,
           exon_end INTEGER NOT NULL,
           FOREIGN KEY (exon_chrom) REFERENCES chrominfo (chrom)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE cds (
           _cds_id INTEGER PRIMARY KEY,
           cds_name TEXT NULL,
           cds_chrom TEXT NOT NULL,
           cds_strand TEXT NOT NULL,
           cds_start INTEGER NOT NULL,
           cds_end INTEGER NOT NULL,
           FOREIGN KEY (cds_chrom) REFERENCES chrominfo (chrom)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE splicing (
           _tx_id INTEGER NOT NULL,
           exon_rank INTEGER NOT NULL,
           _exon_id INTEGER NOT NULL,
           _cds_id INTEGER NULL,
           cds_phase INTEGER NULL,
           UNIQUE (_tx_id, exon_rank),
           FOREIGN KEY (_tx_id) REFERENCES transcript,
           FOREIGN KEY (_exon_id) REFERENCES exon,
           FOREIGN KEY (_cds_id) REFERENCES cds
        )
    """)
    
    cursor.execute("""
        CREATE TABLE gene (
           gene_id TEXT NOT NULL,
           _tx_id INTEGER NOT NULL,
           UNIQUE (gene_id, _tx_id),
           FOREIGN KEY (_tx_id) REFERENCES transcript
        )
    """)
    
    cursor.execute("""
        CREATE TABLE metadata (
          name TEXT,
          value TEXT
        )
    """)
    
    # Insert chromosomes
    print(f"Inserting {num_chroms} chromosomes...")
    chrom_lengths = {
        'chr1': 248956422, 'chr2': 242193529, 'chr3': 198295559,
        'chr4': 190214555, 'chr5': 181538259, 'chr6': 170805979,
        'chr7': 159345973, 'chr8': 145138636, 'chr9': 138394717,
        'chr10': 133797422, 'chrX': 156040895, 'chrY': 57227415,
        'chrM': 16569
    }
    
    chroms = list(chrom_lengths.keys())[:num_chroms]
    
    for i, chrom in enumerate(chroms, 1):
        cursor.execute(
            "INSERT INTO chrominfo VALUES (?, ?, ?, ?)",
            (i, chrom, chrom_lengths[chrom], 1 if chrom == 'chrM' else 0)
        )
    
    # Insert genes and transcripts
    print(f"Inserting {num_genes} genes with transcripts...")
    tx_types = ['protein_coding', 'lncRNA', 'miRNA', 'pseudogene']
    strands = ['+', '-']
    
    tx_id = 1
    exon_id = 1
    cds_id = 1
    
    for gene_num in range(1, num_genes + 1):
        gene_id = f"GENE{gene_num:05d}"
        chrom = random.choice(chroms)
        strand = random.choice(strands)
        
        # Random gene location
        gene_start = random.randint(10000, chrom_lengths[chrom] - 100000)
        gene_length = random.randint(5000, 50000)
        
        # Create transcripts for this gene
        num_tx = random.randint(1, num_transcripts_per_gene)
        
        for tx_num in range(num_tx):
            tx_name = f"{gene_id}.{tx_num + 1}"
            tx_type = random.choice(tx_types)
            
            # Transcript boundaries within gene
            tx_start = gene_start + random.randint(0, 1000)
            tx_end = tx_start + random.randint(2000, gene_length)
            
            cursor.execute(
                "INSERT INTO transcript VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tx_id, tx_name, tx_type, chrom, strand, tx_start, tx_end)
            )
            
            # Link to gene
            cursor.execute(
                "INSERT INTO gene VALUES (?, ?)",
                (gene_id, tx_id)
            )
            
            # Create exons
            num_exons = random.randint(2, 8)
            exon_positions = sorted([
                tx_start + int((tx_end - tx_start) * i / num_exons) 
                for i in range(num_exons + 1)
            ])
            
            for exon_rank in range(num_exons):
                exon_start = exon_positions[exon_rank]
                exon_end = exon_positions[exon_rank + 1]
                exon_name = f"{tx_name}.exon{exon_rank + 1}"
                
                cursor.execute(
                    "INSERT INTO exon VALUES (?, ?, ?, ?, ?, ?)",
                    (exon_id, exon_name, chrom, strand, exon_start, exon_end)
                )
                
                # Create CDS for protein-coding transcripts (skip first and last exon)
                cds_id_for_exon = None
                if tx_type == 'protein_coding' and 0 < exon_rank < num_exons - 1:
                    cds_name = f"{tx_name}.cds{exon_rank}"
                    cds_start = exon_start + random.randint(0, 50)
                    cds_end = exon_end - random.randint(0, 50)
                    
                    cursor.execute(
                        "INSERT INTO cds VALUES (?, ?, ?, ?, ?, ?)",
                        (cds_id, cds_name, chrom, strand, cds_start, cds_end)
                    )
                    cds_id_for_exon = cds_id
                    cds_id += 1
                
                # Create splicing entry
                cursor.execute(
                    "INSERT INTO splicing VALUES (?, ?, ?, ?, ?)",
                    (tx_id, exon_rank + 1, exon_id, cds_id_for_exon,
                     random.choice([0, 1, 2]) if cds_id_for_exon else None)
                )
                
                exon_id += 1
            
            tx_id += 1
    
    # Insert metadata
    print("Inserting metadata...")
    metadata = [
        ('organism', 'Homo sapiens'),
        ('genome', 'GRCh38'),
        ('annotation_source', 'test_data'),
        ('creation_date', '2024-02-18'),
        ('version', '1.0')
    ]
    
    cursor.executemany("INSERT INTO metadata VALUES (?, ?)", metadata)
    
    # Create indexes for performance
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_transcript_chrom ON transcript(tx_chrom)")
    cursor.execute("CREATE INDEX idx_exon_chrom ON exon(exon_chrom)")
    cursor.execute("CREATE INDEX idx_cds_chrom ON cds(cds_chrom)")
    cursor.execute("CREATE INDEX idx_gene_tx ON gene(_tx_id)")
    cursor.execute("CREATE INDEX idx_splicing_tx ON splicing(_tx_id)")
    
    conn.commit()
    
    # Print statistics
    print("\nDatabase statistics:")
    for table in ['chrominfo', 'transcript', 'exon', 'cds', 'splicing', 'gene', 'metadata']:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:12s}: {count:6d} rows")
    
    # Print file size
    conn.close()
    size_mb = Path(db_path).stat().st_size / (1024 * 1024)
    print(f"\nDatabase file size: {size_mb:.2f} MB")
    print(f"✓ Sample database created: {db_path}")


def main():
    """Main entry point."""
    db_path = sys.argv[1] if len(sys.argv) > 1 else "test_genome.db"
    
    create_sample_database(
        db_path=db_path,
        num_chroms=5,
        num_genes=1000,
        num_transcripts_per_gene=2
    )
    
    print("\nTo convert to Parquet, run:")
    print(f"  python sqlite_to_parquet.py {db_path} parquet_output/")


if __name__ == '__main__':
    main()
