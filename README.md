# Parallel File Word Counter 📊

A high-performance command-line Python tool that counts words in `.txt`, `.csv`, and `.pdf` files within a directory using **multiprocessing** for efficient parallel processing.

## Features

✅ **Parallel Processing** - Utilizes multiple CPU cores for simultaneous file processing  
✅ **Error Handling** - Gracefully handles file read errors and invalid inputs  
✅ **Efficient Output** - Sorted per-file counts + total word count with formatted numbers  
✅ **Smart Process Pool** - Automatically scales to available CPU cores  
✅ **CSV Support** - Reads CSV cells and counts their text content  
✅ **PDF Support** - Extracts text from PDFs with `pypdf`  
✅ **UTF-8 Support** - Handles various text encodings  

## Installation

### Requirements
- Python 3.6+
- `pypdf` for PDF support

### Setup
```bash
# Clone or download the repository
cd path/to/project

# Make the script executable (optional, on Linux/macOS)
chmod +x word_counter.py
```

## Usage

### Basic Usage
```bash
python word_counter.py <directory_path>
```

### Examples
```bash
# Count words in current directory
python word_counter.py .

# Count words in a specific directory
python word_counter.py /path/to/files

# Count words in relative directory
python word_counter.py ./documents
```

### Output Example
```
Processing 3 file(s) with 3 process(es)...
------------------------------------------------------------
sample1.txt                                      68 words
 sample2.csv                                      70 words
 sample3.pdf                                      74 words
------------------------------------------------------------
TOTAL                                           212 words
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Main Process                                   │
│  • Parse command-line arguments                │
│  • Discover supported files in directory       │
│  • Create process pool                          │
└──────────────┬──────────────────────────────────┘
               │
               ├─► Worker Process 1 ──► count_words_in_file(file1.txt)
               │
               ├─► Worker Process 2 ──► count_words_in_file(file2.txt)
               │
               └─► Worker Process 3 ──► count_words_in_file(file3.txt)
               │
               ├─ Results aggregated
               │
┌──────────────▼──────────────────────────────────┐
│  Aggregate & Display Results                    │
│  • Sort results alphabetically                  │
│  • Display per-file counts                      │
│  • Calculate and show total                     │
└─────────────────────────────────────────────────┘
```

### Key Components

1. **`count_words_in_file()`** - Worker function executed by each process
   - Reads a single file
   - Uses format-aware extraction for text, CSV, and PDF files
   - Splits content and counts words
   - Returns filename and count tuple
   - Handles errors gracefully

2. **`get_supported_files()`** - File discovery
   - Uses `pathlib.Path.glob()` for efficient file finding
   - Validates directory existence
   - Returns list of all supported files (`.txt`, `.csv`, `.pdf`)

3. **`main()`** - Orchestration
   - Initializes process pool (up to `cpu_count()`)
   - Maps worker function across files
   - Aggregates results
   - Displays formatted output

### Performance Considerations

| Aspect | Details |
|--------|---------|
| **Parallelization** | Uses `multiprocessing.Pool` for true parallelism (CPU cores, not threads) |
| **Process Count** | Auto-scaled to `min(cpu_count(), num_files)` to avoid overhead |
| **I/O Handling** | File I/O is blocking but happens in separate processes—doesn't block UI |
| **Memory** | Each process has independent memory space; minimal shared state |

## Files Included

- `word_counter.py` - Main implementation
- `sample1.txt`, `sample2.txt`, `sample3.txt` - Test files
- `README.md` - This documentation
- `word_counter_advanced.py` - Enhanced version with additional features

## Advanced Version

The `word_counter_advanced.py` includes:
- **Recursive directory scanning** (`-r` flag)
- **Multiple file extensions** (including `.txt`, `.csv`, `.pdf`)
- **Configurable process pool size**
- **Timing statistics**
- **Progress bar** (for visual feedback)
- **JSON output option**

Usage:
```bash
python word_counter_advanced.py . -r -e txt md py -o results.json
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Missing directory argument | Displays usage message and exits with code 1 |
| Invalid directory path | Prints error message and exits with code 1 |
| No supported files found | Prints warning and exits gracefully |
| File read error | Prints error to stderr, counts as 0 words, continues |
| Encoding issues | Uses `errors='ignore'` to handle non-UTF-8 files |

### PDF Support

PDF files require `pypdf`:
```bash
pip install pypdf
```

## Troubleshooting

### "Command not found: python"
Use `python3` instead on some systems:
```bash
python3 word_counter.py .
```

### No output / slow performance
- Ensure `.txt` files exist in the directory
- Check file permissions
- Large files may take longer to process

### Memory issues with many files
Reduce pool size in advanced version:
```bash
python word_counter_advanced.py . -p 4
```

## Learning Outcomes

This project teaches:
✓ Multiprocessing and process pools  
✓ Process-based parallelism vs threading  
✓ Work distribution and aggregation  
✓ Error handling in concurrent code  
✓ File system operations with `pathlib`  
✓ Command-line argument parsing  
✓ Data serialization for inter-process communication  

## License

Free to use and modify for educational purposes.
