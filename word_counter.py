 

import os
import sys
import csv
from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import Tuple

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

SUPPORTED_EXTENSIONS = ('.txt', '.csv', '.pdf')


def read_file_content(file_path: str) -> str:
    file_path_obj = Path(file_path)
    suffix = file_path_obj.suffix.lower()

    if suffix == '.pdf':
        if PdfReader is None:
            raise ImportError(
                'PDF support requires the pypdf package. Install it with: pip install pypdf'
            )

        reader = PdfReader(str(file_path_obj))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or '')
        return '\n'.join(pages)

    if suffix == '.csv':
        rows = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(' '.join(cell.strip() for cell in row if cell.strip()))
        return '\n'.join(rows)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def count_words_in_file(file_path: str) -> Tuple[str, int]:
     
    try:
        content = read_file_content(file_path)
        word_count = len(content.split())
        return (os.path.basename(file_path), word_count)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return (os.path.basename(file_path), 0)


def get_supported_files(directory: str) -> list:
    path = Path(directory)
    if not path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a valid directory")
    
    files = []
    for extension in SUPPORTED_EXTENSIONS:
        files.extend(path.glob(f'*{extension}'))

    if not files:
        extensions_text = ', '.join(SUPPORTED_EXTENSIONS)
        print(f"No supported files ({extensions_text}) found in '{directory}'", file=sys.stderr)
        return []
    
    return [str(f) for f in sorted(files)]


def main():
    """Main entry point for the word counter tool."""
    # Validate command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python word_counter.py <directory_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
 
    try:
        txt_files = get_supported_files(directory)
    except NotADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not txt_files:
        sys.exit(0)
     
    num_processes = min(cpu_count(), len(txt_files))
    
    print(f"Processing {len(txt_files)} file(s) with {num_processes} process(es)...")
    print("-" * 60)
    
    # Process files in parallel
    with Pool(processes=num_processes) as pool:
        results = pool.map(count_words_in_file, txt_files)
  
    total_words = 0
    for filename, word_count in sorted(results):
        print(f"{filename:<40} {word_count:>10,} words")
        total_words += word_count
   
    print("-" * 60)
    print(f"{'TOTAL':<40} {total_words:>10,} words")


if __name__ == '__main__':
    main()
