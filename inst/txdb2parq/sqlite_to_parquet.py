#!/usr/bin/env python3
"""
SQLite to Parquet Converter using DuckDB

This script efficiently converts SQLite database tables to Parquet format using
DuckDB's zero-copy export capabilities. Particularly well-suited for genomic
annotation databases.

Usage:
    python sqlite_to_parquet.py input.db output_dir/
    python sqlite_to_parquet.py input.db output_dir/ --tables transcript exon
    python sqlite_to_parquet.py input.db output_dir/ --compression zstd --level 6
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional
import duckdb


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SQLiteToParquetConverter:
    """Convert SQLite database tables to Parquet format using DuckDB."""
    
    VALID_COMPRESSIONS = ['uncompressed', 'snappy', 'gzip', 'zstd', 'lz4']
    
    def __init__(
        self,
        sqlite_path: str,
        output_dir: str,
        compression: str = 'zstd',
        compression_level: Optional[int] = None,
        row_group_size: int = 122880,
        overwrite: bool = False
    ):
        """
        Initialize the converter.
        
        Args:
            sqlite_path: Path to the SQLite database file
            output_dir: Directory where Parquet files will be written
            compression: Compression codec (uncompressed, snappy, gzip, zstd, lz4)
            compression_level: Compression level (codec-dependent, None for default)
            row_group_size: Number of rows per row group
            overwrite: Whether to overwrite existing Parquet files
        """
        self.sqlite_path = Path(sqlite_path)
        self.output_dir = Path(output_dir)
        self.compression = compression.lower()
        self.compression_level = compression_level
        self.row_group_size = row_group_size
        self.overwrite = overwrite
        
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate input parameters."""
        if not self.sqlite_path.exists():
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")
        
        if not self.sqlite_path.is_file():
            raise ValueError(f"Not a file: {self.sqlite_path}")
        
        if self.compression not in self.VALID_COMPRESSIONS:
            raise ValueError(
                f"Invalid compression: {self.compression}. "
                f"Must be one of: {', '.join(self.VALID_COMPRESSIONS)}"
            )
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir.absolute()}")
    
    def get_table_list(self, con: duckdb.DuckDBPyConnection) -> List[str]:
        """
        Get list of all tables in the SQLite database.
        
        Args:
            con: DuckDB connection
            
        Returns:
            List of table names
        """
        # Use SHOW TABLES which works correctly with attached SQLite databases
        # Note: SHOW TABLES returns a column named 'name', not 'table_name'
        result = con.execute(
            "SELECT name FROM (SHOW TABLES FROM sqlite_db)"
        ).fetchall()
        
        tables = [row[0] for row in result]
        return sorted(tables)
    
    def get_table_info(
        self, 
        con: duckdb.DuckDBPyConnection, 
        table_name: str
    ) -> dict:
        """
        Get information about a table.
        
        Args:
            con: DuckDB connection
            table_name: Name of the table
            
        Returns:
            Dictionary with table metadata
        """
        # Get row count
        row_count = con.execute(
            f"SELECT COUNT(*) FROM sqlite_db.{table_name}"
        ).fetchone()[0]
        
        # Get column info using DESCRIBE
        schema = con.execute(
            f"DESCRIBE sqlite_db.{table_name}"
        ).fetchall()
        
        return {
            'row_count': row_count,
            'column_count': len(schema),
            'columns': schema
        }
    
    def convert_table(
        self,
        con: duckdb.DuckDBPyConnection,
        table_name: str
    ) -> dict:
        """
        Convert a single table to Parquet format.
        
        Args:
            con: DuckDB connection
            table_name: Name of the table to convert
            
        Returns:
            Dictionary with conversion statistics
        """
        output_path = self.output_dir / f"{table_name}.parquet"
        
        # Check if file exists and handle overwrite
        if output_path.exists() and not self.overwrite:
            logger.warning(
                f"Skipping {table_name}: {output_path} already exists. "
                f"Use --overwrite to replace."
            )
            return {'status': 'skipped', 'reason': 'file_exists'}
        
        logger.info(f"Converting table: {table_name}")
        
        # Get table info
        try:
            info = self.get_table_info(con, table_name)
            logger.info(
                f"  Rows: {info['row_count']:,}, "
                f"Columns: {info['column_count']}"
            )
        except Exception as e:
            logger.warning(f"  Could not get table info: {e}")
            info = {'row_count': None}
        
        # Build COPY command with compression options
        compression_opts = f"COMPRESSION '{self.compression.upper()}'"
        if self.compression_level is not None:
            compression_opts += f", COMPRESSION_LEVEL {self.compression_level}"
        
        copy_sql = f"""
            COPY sqlite_db.{table_name}
            TO '{output_path}'
            (
                FORMAT PARQUET,
                {compression_opts},
                ROW_GROUP_SIZE {self.row_group_size}
            )
        """
        
        try:
            # Execute conversion
            con.execute(copy_sql)
            
            # Get output file size
            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(
                f"  ✓ Completed: {output_path.name} "
                f"({file_size_mb:.2f} MB)"
            )
            
            return {
                'status': 'success',
                'row_count': info['row_count'],
                'file_size': file_size,
                'file_size_mb': file_size_mb,
                'output_path': str(output_path)
            }
            
        except Exception as e:
            logger.error(f"  ✗ Failed to convert {table_name}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def convert_all(
        self, 
        table_filter: Optional[List[str]] = None
    ) -> dict:
        """
        Convert all tables (or filtered subset) to Parquet.
        
        Args:
            table_filter: Optional list of table names to convert.
                         If None, converts all tables.
        
        Returns:
            Dictionary with overall conversion statistics
        """
        logger.info(f"Starting conversion from: {self.sqlite_path}")
        logger.info(f"Compression: {self.compression}" + 
                   (f" (level {self.compression_level})" 
                    if self.compression_level else ""))
        
        # Connect to DuckDB and attach SQLite database
        con = duckdb.connect()
        
        try:
            logger.info("Attaching SQLite database...")
            con.execute(
                f"ATTACH '{self.sqlite_path}' AS sqlite_db (TYPE SQLITE)"
            )
            
            # Get list of tables
            all_tables = self.get_table_list(con)
            logger.info(f"Found {len(all_tables)} tables: {', '.join(all_tables)}")
            
            # Apply filter if provided
            if table_filter:
                tables_to_convert = [t for t in table_filter if t in all_tables]
                missing_tables = set(table_filter) - set(all_tables)
                
                if missing_tables:
                    logger.warning(
                        f"Tables not found in database: {', '.join(missing_tables)}"
                    )
                
                if not tables_to_convert:
                    raise ValueError("No valid tables to convert")
                
                logger.info(
                    f"Converting {len(tables_to_convert)} table(s): "
                    f"{', '.join(tables_to_convert)}"
                )
            else:
                tables_to_convert = all_tables
            
            # Convert each table
            results = {}
            total_size = 0
            success_count = 0
            
            for table in tables_to_convert:
                result = self.convert_table(con, table)
                results[table] = result
                
                if result['status'] == 'success':
                    success_count += 1
                    total_size += result['file_size']
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("CONVERSION SUMMARY")
            logger.info("="*60)
            logger.info(f"Total tables processed: {len(tables_to_convert)}")
            logger.info(f"Successful: {success_count}")
            logger.info(f"Failed: {len([r for r in results.values() if r['status'] == 'failed'])}")
            logger.info(f"Skipped: {len([r for r in results.values() if r['status'] == 'skipped'])}")
            logger.info(f"Total output size: {total_size / (1024*1024):.2f} MB")
            logger.info("="*60)
            
            return {
                'tables_processed': len(tables_to_convert),
                'success_count': success_count,
                'total_size_mb': total_size / (1024*1024),
                'results': results
            }
            
        finally:
            con.close()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert SQLite database tables to Parquet format using DuckDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all tables with default settings
  %(prog)s genome.db parquet_output/
  
  # Convert specific tables only
  %(prog)s genome.db parquet_output/ --tables transcript exon cds
  
  # Use maximum compression
  %(prog)s genome.db parquet_output/ --compression zstd --level 9
  
  # Use fast compression
  %(prog)s genome.db parquet_output/ --compression snappy
  
  # Overwrite existing files
  %(prog)s genome.db parquet_output/ --overwrite
  
Compression options:
  - uncompressed: No compression (fastest, largest files)
  - snappy: Fast compression, moderate size (good default)
  - gzip: Good compression, slower
  - zstd: Best compression/speed balance (recommended)
  - lz4: Very fast, moderate compression
        """
    )
    
    parser.add_argument(
        'sqlite_db',
        help='Path to SQLite database file'
    )
    
    parser.add_argument(
        'output_dir',
        help='Output directory for Parquet files'
    )
    
    parser.add_argument(
        '--tables',
        nargs='+',
        metavar='TABLE',
        help='Specific table names to convert (default: all tables)'
    )
    
    parser.add_argument(
        '--compression',
        choices=['uncompressed', 'snappy', 'gzip', 'zstd', 'lz4'],
        default='zstd',
        help='Compression codec (default: zstd)'
    )
    
    parser.add_argument(
        '--level',
        type=int,
        metavar='N',
        help='Compression level (codec-dependent, e.g., 1-9 for zstd)'
    )
    
    parser.add_argument(
        '--row-group-size',
        type=int,
        default=122880,
        metavar='N',
        help='Rows per row group (default: 122880)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing Parquet files'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress informational output'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Adjust logging level
    if args.quiet:
        logger.setLevel(logging.WARNING)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Create converter
        converter = SQLiteToParquetConverter(
            sqlite_path=args.sqlite_db,
            output_dir=args.output_dir,
            compression=args.compression,
            compression_level=args.level,
            row_group_size=args.row_group_size,
            overwrite=args.overwrite
        )
        
        # Run conversion
        results = converter.convert_all(table_filter=args.tables)
        
        # Exit with appropriate code
        if results['success_count'] == results['tables_processed']:
            logger.info("✓ All conversions completed successfully")
            sys.exit(0)
        else:
            logger.warning("⚠ Some conversions failed or were skipped")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(2)


if __name__ == '__main__':
    main()

