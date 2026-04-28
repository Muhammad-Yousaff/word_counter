#!/usr/bin/env python3
"""
Parallel File Word Counter

A command-line tool that counts words in all .txt files within a directory
using multiprocessing for efficient parallel processing.

Usage:
    python word_counter.py <directory_path>
"""

import os
import sys
from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import Tuple


def count_words_in_file(file_path: str) -> Tuple[str, int]:
    """
    Count the number of words in a single file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple of (filename, word_count)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            word_count = len(content.split())
        return (os.path.basename(file_path), word_count)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return (os.path.basename(file_path), 0)


def get_txt_files(directory: str) -> list:
    """
    Get all .txt files in a directory.
    
    Args:
        directory: Path to the directory
        
    Returns:
        List of absolute file paths
    """
    path = Path(directory)
    if not path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a valid directory")
    
    txt_files = list(path.glob('*.txt'))
    if not txt_files:
        print(f"No .txt files found in '{directory}'", file=sys.stderr)
        return []
    
    return [str(f) for f in txt_files]


def main():
    """Main entry point for the word counter tool."""
    # Validate command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python word_counter.py <directory_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # Get all .txt files
    try:
        txt_files = get_txt_files(directory)
    except NotADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not txt_files:
        sys.exit(0)
    
    # Determine number of processes
    num_processes = min(cpu_count(), len(txt_files))
    
    print(f"Processing {len(txt_files)} file(s) with {num_processes} process(es)...")
    print("-" * 60)
    
    # Process files in parallel
    with Pool(processes=num_processes) as pool:
        results = pool.map(count_words_in_file, txt_files)
    
    # Display per-file results
    total_words = 0
    for filename, word_count in sorted(results):
        print(f"{filename:<40} {word_count:>10,} words")
        total_words += word_count
    
    # Display total
    print("-" * 60)
    print(f"{'TOTAL':<40} {total_words:>10,} words")


if __name__ == '__main__':
    main()
