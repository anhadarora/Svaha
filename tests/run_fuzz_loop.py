import subprocess
import os
import sys

def main():
    """
    Runs a UI fuzz test for a specified screen.
    The test itself is responsible for running a set of scenarios or permutations.
    This script simply provides a convenient entry point.

    Usage: python run_fuzz_loop.py <screen_name>
    Example: python run_fuzz_loop.py downloader
    """
    if len(sys.argv) < 2:
        print("Usage: python run_fuzz_loop.py <screen_name>")
        print("Example: python run_fuzz_loop.py downloader")
        sys.exit(1)
        
    screen_name = sys.argv[1]
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Construct the test file path dynamically
    test_file_path = os.path.join(project_root, 'tests', f'test_fuzz_{screen_name}.py')
    
    if not os.path.exists(test_file_path):
        print(f"Error: Test file not found at '{test_file_path}'")
        sys.exit(1)

    python_executable = os.path.join(project_root, 'venv', 'bin', 'python')
    
    print(f"--- Starting Test Suite for '{screen_name}' ---")
    
    command = [
        python_executable,
        "-m",
        "pytest",
        test_file_path,
    ]
    
    # Run the test process in the foreground to see the output
    process = subprocess.run(command, text=True, cwd=project_root)
    
    exit_code = process.returncode
    
    if exit_code == 0:
        print(f"--- Test Suite for '{screen_name}' PASSED ---")
    else:
        print(f"--- Test Suite for '{screen_name}' FAILED (Exit Code: {exit_code}) ---")
        print("See pytest output above for details.")

if __name__ == "__main__":
    main()
