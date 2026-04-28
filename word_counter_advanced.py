#!/usr/bin/env python3
"""
Advanced Parallel File Word Counter

An enhanced version with features like:
- Recursive directory scanning
- Multiple file extensions
- Progress tracking
- JSON output
- Configurable process pool size

Usage:
    python word_counter_advanced.py <directory_path> [options]
    
Options:
    -r, --recursive         Recursively scan subdirectories
    -e, --extensions        File extensions to process (default: txt)
    -p, --processes         Number of processes (default: auto)
    -o, --output            Output to JSON file
    -v, --verbose           Verbose output with timing stats
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import Tuple, Dict, List


def count_words_in_file(file_path: str) -> Tuple[str, int, int]:
    """
    Count the number of words in a single file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple of (relative_path, word_count, file_size_bytes)
    """
    try:
        file_path_obj = Path(file_path)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            word_count = len(content.split())
        file_size = file_path_obj.stat().st_size
        return (str(file_path_obj), word_count, file_size)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return (str(file_path), 0, 0)


def get_files_by_extension(directory: str, extensions: List[str], 
                           recursive: bool = False) -> List[str]:
    """
    Get all files with specified extensions in a directory.
    
    Args:
        directory: Path to the directory
        extensions: List of file extensions (without dots)
        recursive: Whether to search subdirectories
        
    Returns:
        List of absolute file paths
    """
    path = Path(directory)
    if not path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a valid directory")
    
    files = []
    for ext in extensions:
        pattern = f'**/*.{ext}' if recursive else f'*.{ext}'
        files.extend(path.glob(pattern))
    
    if not files:
        extensions_str = ', '.join(f'.{e}' for e in extensions)
        print(f"No files with extensions {extensions_str} found in '{directory}'", 
              file=sys.stderr)
        return []
    
    return sorted([str(f) for f in files])


def format_bytes(bytes_count: int) -> str:
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"


def main():
    """Main entry point for the advanced word counter tool."""
    parser = argparse.ArgumentParser(
        description='Count words in files using multiprocessing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Recursively scan subdirectories')
    parser.add_argument('-e', '--extensions', nargs='+', default=['txt'],
                        help='File extensions to process (default: txt)')
    parser.add_argument('-p', '--processes', type=int, default=None,
                        help='Number of processes (default: auto)')
    parser.add_argument('-o', '--output', help='Output results to JSON file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output with timing stats')
    
    args = parser.parse_args()
    
    # Clean extensions (remove leading dots if present)
    extensions = [ext.lstrip('.') for ext in args.extensions]
    
    # Get all files
    try:
        files = get_files_by_extension(args.directory, extensions, args.recursive)
    except NotADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not files:
        sys.exit(0)
    
    # Determine number of processes
    num_processes = args.processes or min(cpu_count(), len(files))
    num_processes = max(1, min(num_processes, len(files)))
    
    # Display info
    recursive_text = " (recursive)" if args.recursive else ""
    ext_text = ", ".join(f".{e}" for e in extensions)
    print(f"Scanning for {ext_text} files{recursive_text}...")
    print(f"Processing {len(files)} file(s) with {num_processes} process(es)...")
    print("-" * 80)
    
    # Track timing
    start_time = time.time()
    
    # Process files in parallel
    with Pool(processes=num_processes) as pool:
        results = pool.map(count_words_in_file, files)
    
    elapsed_time = time.time() - start_time
    
    # Aggregate results
    total_words = 0
    total_size = 0
    file_results = []
    
    for filepath, word_count, file_size in sorted(results):
        total_words += word_count
        total_size += file_size
        file_results.append({
            'file': filepath,
            'words': word_count,
            'size': file_size
        })
        
        # Display per-file result
        size_str = format_bytes(file_size)
        print(f"{filepath:<50} {word_count:>10,} words ({size_str:>12})")
    
    # Display totals
    print("-" * 80)
    total_size_str = format_bytes(total_size)
    print(f"{'TOTAL':<50} {total_words:>10,} words ({total_size_str:>12})")
    
    # Verbose stats
    if args.verbose:
        print("-" * 80)
        avg_words_per_file = total_words // len(files) if files else 0
        avg_size_per_file = total_size // len(files) if files else 0
        throughput = len(files) / elapsed_time if elapsed_time > 0 else 0
        print(f"Time elapsed:          {elapsed_time:.2f} seconds")
        print(f"Files processed:       {len(files)}")
        print(f"Avg words per file:    {avg_words_per_file:,}")
        print(f"Avg size per file:     {format_bytes(avg_size_per_file)}")
        print(f"Processing rate:       {throughput:.1f} files/sec")
    
    # JSON output
    if args.output:
        output_data = {
            'directory': str(Path(args.directory).resolve()),
            'recursive': args.recursive,
            'extensions': extensions,
            'total_files': len(files),
            'total_words': total_words,
            'total_bytes': total_size,
            'total_size_human': total_size_str,
            'elapsed_seconds': elapsed_time,
            'files': file_results
        }
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nResults saved to: {args.output}")
        except Exception as e:
            print(f"Error saving JSON output: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
