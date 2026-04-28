# Technical Documentation: Parallel File Word Counter

## Architecture Deep Dive

### Why Multiprocessing?

In Python, the **Global Interpreter Lock (GIL)** prevents true parallelism with threads. This tool uses **multiprocessing** instead:

- **Threads**: Share memory, but only one executes at a time (I/O bound tasks)
- **Processes**: Separate memory spaces, true CPU parallelism (CPU bound tasks)
- **Multiprocessing**: Ideal for CPU-intensive work across multiple CPU cores

### Process Pool Design

```
Main Process                  Worker Processes
    │                         ┌─ Process 1
    │                         │
    ├─ Get .txt files         ├─ Process 2
    │                         │
    ├─ Create Pool(N)   ────> ├─ Process 3
    │                         │
    ├─ Map tasks              └─ Process 4
    │
    └─ Aggregate results <──── Return (filename, word_count)
```

### Implementation Details

#### 1. Worker Function: `count_words_in_file()`

```python
def count_words_in_file(file_path: str) -> Tuple[str, int]:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        word_count = len(content.split())
    return (os.path.basename(file_path), word_count)
```

**Why this works:**
- Functions passed to `pool.map()` must be **picklable** (serializable)
- Lambda functions and nested functions are NOT picklable
- Module-level functions work reliably
- Each process gets its own copy of the function code

#### 2. Pool Sizing Strategy

```python
num_processes = min(cpu_count(), len(txt_files))
```

**Rationale:**
- Don't create more processes than CPU cores (overhead)
- Don't create more than files to process (idle processes)
- Typical optimal: N = number of CPU cores

**Example:**
- 8-core CPU, 3 files → Use 3 processes (less overhead than 8)
- 4-core CPU, 100 files → Use 4 processes (distribute among cores)

#### 3. Data Flow: map() and Aggregation

```python
with Pool(processes=num_processes) as pool:
    results = pool.map(count_words_in_file, txt_files)
```

**What `pool.map()` does:**
1. **Chunk** the input list (files) across processes
2. **Apply** the function to each chunk in parallel
3. **Gather** results in original order
4. **Return** list of results as if sequential

**Process:**
```
Input:  [file1.txt, file2.txt, file3.txt, file4.txt]
        ↓ (distribute to 4 processes)
        
Process 1: file1.txt → (file1.txt, 150)
Process 2: file2.txt → (file2.txt, 200)
Process 3: file3.txt → (file3.txt, 175)
Process 4: file4.txt → (file4.txt, 225)
        ↓ (gather in order)
Output: [(file1.txt, 150), (file2.txt, 200), (file3.txt, 175), (file4.txt, 225)]
```

#### 4. Inter-Process Communication (IPC)

Python's multiprocessing uses **serialization (pickling)** for IPC:

```
Main Process                Worker Process
    │
    │ pickle
    ├──────────────────────> file_path (string)
    │
    │                        count_words_in_file(file_path)
    │                        ↓
    │                        return (filename, count)
    │
    │                        pickle
    │ <──────────────────────
    │ unpickle
    │
Results in original order
```

**Serializable objects:** int, str, list, dict, tuple, bytes, etc.
**Non-serializable:** file handles, locks, connections

### Performance Analysis

#### Time Complexity
- **Sequential:** O(n × m) where n = files, m = avg. file size
- **Parallel:** O((n × m) / p) where p = processes (approximately)
- **Overhead:** Process creation ~50ms each, serialization overhead

#### Memory Usage
- **Per process:** ~25-50 MB base Python runtime
- **4 processes:** ~200-300 MB overhead
- **File caching:** Each file read once per process (no duplication)

#### Speedup Example (4-core system)

| Metric | Sequential | Parallel (4) | Speedup |
|--------|-----------|--------------|---------|
| 100 × 1MB files | 15.2 sec | 4.1 sec | 3.7× |
| 1000 × 100KB files | 8.5 sec | 2.3 sec | 3.7× |

**Note:** Speedup < 4× due to:
- Process creation overhead
- File I/O serialization
- Memory bandwidth limits

### Error Handling Strategy

```python
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        word_count = len(f.read().split())
    return (filename, word_count)
except Exception as e:
    print(f"Error reading {file_path}: {e}")
    return (filename, 0)  # Graceful degradation
```

**Why this approach:**
- One bad file doesn't crash entire process
- Errors logged to stderr
- Process continues with other files
- Bad files counted as 0 words

### Advanced Version Features

#### 1. Recursive Directory Scanning

```python
# Non-recursive: pattern = '*.txt'
files = path.glob('*.txt')

# Recursive: pattern = '**/*.txt'
files = path.glob('**/*.txt')
```

**Behavior:**
```
directory/
  ├─ file1.txt          ✓ (both match)
  └─ subdir/
     └─ file2.txt       ✓ (only ** matches)
```

#### 2. Multiple File Extensions

```python
extensions = ['txt', 'md', 'py']
for ext in extensions:
    pattern = f'**/*.{ext}' if recursive else f'*.{ext}'
    files.extend(path.glob(pattern))
```

#### 3. Timing Measurements

```python
start = time.time()
# ... processing ...
elapsed = time.time() - start
throughput = len(files) / elapsed  # files/sec
```

**Useful metrics:**
- Wall-clock time (total elapsed)
- Throughput (files processed per second)
- Avg time per file

#### 4. JSON Output Format

```json
{
  "directory": "/path/to/dir",
  "recursive": false,
  "extensions": ["txt"],
  "total_files": 3,
  "total_words": 212,
  "total_bytes": 1768,
  "elapsed_seconds": 0.44,
  "files": [
    {"file": "file1.txt", "words": 68, "size": 547},
    {"file": "file2.txt", "words": 70, "size": 586}
  ]
}
```

### Platform Differences

#### Windows
- `if __name__ == '__main__':` **REQUIRED** for multiprocessing
- Freezegun and other mocking libs may interfere
- Process spawning uses `spawn` (not `fork`)

#### Linux/macOS
- `if __name__ == '__main__':` still recommended
- Faster with `fork` context (default)
- Better multiprocessing performance

### Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| **ImportError in worker process** | Move imports to top of module |
| **Function not found in worker** | Define at module level, not in `main()` |
| **Memory grows with processes** | Limit pool size, don't create 1000 processes |
| **Results out of order** | Use `imap_unordered()` for speed, reorder if needed |
| **Slow on small datasets** | Overhead > benefit, use sequential for <10 files |

### Testing Recommendations

```python
# Unit test worker function
assert count_words_in_file('sample.txt') == ('sample.txt', 68)

# Integration test with pool
with Pool(2) as pool:
    results = pool.map(count_words_in_file, test_files)
    assert sum(r[1] for r in results) == expected_total

# Stress test
# - 1000s of files
# - Very large files (>1GB)
# - Symlinks and special chars in names
# - Permission denied scenarios
```

### Production Considerations

1. **Logging:** Use `multiprocessing.log_to_stderr()` for debugging
2. **Graceful shutdown:** Use context manager (`with Pool()...`)
3. **Signal handling:** Handle SIGTERM in workers
4. **Timeouts:** Consider `pool.map_async()` with timeout
5. **Resource limits:** Monitor memory and CPU usage
6. **Error tracking:** Aggregate error counts from workers

### Further Reading

- [Python Multiprocessing Documentation](https://docs.python.org/3/library/multiprocessing.html)
- [GIL and Parallelism](https://realpython.com/python-gil/)
- [Process Pool Best Practices](https://docs.python.org/3/library/concurrent.futures.html)
- [Pickle Protocol](https://docs.python.org/3/library/pickle.html)
