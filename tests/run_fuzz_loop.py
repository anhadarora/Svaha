import subprocess
import os
import shutil
from datetime import datetime
import time

def main():
    """
    Runs the UI fuzz test in a loop, captures crash reports, and restarts.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    crashes_dir = os.path.join(project_root, 'crashes')
    history_file_path = os.path.join(project_root, 'fuzz_history.json')
    
    # Ensure the python executable from the venv is used
    python_executable = os.path.join(project_root, 'venv', 'bin', 'python')
    
    # Create the crashes directory if it doesn't exist
    os.makedirs(crashes_dir, exist_ok=True)
    
    run_count = 0
    while True:
        run_count += 1
        print(f"--- Starting Fuzz Test Run #{run_count} ---")
        
        # Command to run pytest for the specific fuzz test file
        command = [
            python_executable,
            "-m",
            "pytest",
            os.path.join(project_root, 'tests', 'test_fuzz_trainer.py'),
            "--json-report", # Optional: creates a json report of test status
        ]
        
        # Run the test process
        process = subprocess.run(command, capture_output=True, text=True, cwd=project_root)
        
        exit_code = process.returncode
        
        # --- Outcome Analysis ---
        if exit_code == 0:
            print(f"Run #{run_count} completed successfully (Exit Code: 0).")
        elif exit_code == 1:
            print(f"Run #{run_count} failed with a standard test failure (Exit Code: 1).")
        else:
            # Any other exit code is treated as a hard crash (e.g., segfault)
            print(f"!!! Run #{run_count} appears to have crashed (Exit Code: {exit_code}) !!!")
            print("--- STDOUT ---")
            print(process.stdout)
            print("--- STDERR ---")
            print(process.stderr)
            print("--------------")

        # --- Artifact Management ---
        if os.path.exists(history_file_path):
            if exit_code != 0:
                # A failure or crash occurred, so save the history log.
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"crash_{timestamp}_code{exit_code}.json"
                destination_path = os.path.join(crashes_dir, new_filename)
                
                try:
                    shutil.move(history_file_path, destination_path)
                    print(f"Saved crash log to: {destination_path}")
                except Exception as e:
                    print(f"Error moving history file: {e}")
            else:
                # Run was successful, clean up the history file.
                try:
                    os.remove(history_file_path)
                except Exception as e:
                    print(f"Error removing history file after successful run: {e}")

        # Short delay before the next run
        time.sleep(1)

if __name__ == "__main__":
    main()
