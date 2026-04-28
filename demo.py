#!/usr/bin/env python3
"""
Demo script showcasing the word counter tools
Run this to see various usage examples
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print("\n" + "="*80)
    print(f"📌 {description}")
    print("="*80)
    print(f"$ {cmd}\n")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"⚠️  Command exited with code {result.returncode}")
    except Exception as e:
        print(f"❌ Error running command: {e}")


def main():
    """Run demo examples."""
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  PARALLEL FILE WORD COUNTER - DEMO  ".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Demo 1: Basic usage
    run_command(
        "python word_counter.py .",
        "Example 1: Basic word counter (current directory)"
    )
    
    # Demo 2: Advanced with verbose
    run_command(
        "python word_counter_advanced.py . -v",
        "Example 2: Advanced version with timing statistics"
    )
    
    # Demo 3: JSON output
    run_command(
        "python word_counter_advanced.py . -o demo_results.json && echo. && echo JSON output saved!",
        "Example 3: Generate JSON output"
    )
    
    # Demo 4: Multiple extensions (if other file types exist)
    run_command(
        "python word_counter_advanced.py . -e txt py -v",
        "Example 4: Count words in .txt and .py files"
    )
    
    # Demo 5: Help
    run_command(
        "python word_counter_advanced.py --help",
        "Example 5: View all available options"
    )
    
    print("\n" + "="*80)
    print("✅ Demo completed!")
    print("="*80)
    print("\n📚 Key Learnings:")
    print("  • Multiprocessing for true parallelism (vs threading)")
    print("  • Process pool for work distribution")
    print("  • Data aggregation from parallel workers")
    print("  • Command-line argument parsing with argparse")
    print("  • File system operations with pathlib")
    print("  • JSON serialization for structured output")
    print("\n💡 Try these commands yourself:")
    print("  python word_counter.py .")
    print("  python word_counter_advanced.py . -v")
    print("  python word_counter_advanced.py . -r (recursive)")
    print("\n")


if __name__ == '__main__':
    main()
