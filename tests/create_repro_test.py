
import argparse
import json
import os
import re
import shutil

def create_repro_test(crash_log_path):
    """
    Creates a reproducible test case from a chaos monkey crash log.

    Args:
        crash_log_path (str): The path to the crash log JSON file.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_path = os.path.join(project_root, 'tests', 'test_chaos_trainer.py')
    repro_dir = os.path.join(project_root, 'tests', 'repro')

    # 1. Ensure the template file exists
    if not os.path.exists(template_path):
        print(f"Error: Template test file not found at {template_path}")
        return

    # 2. Read the crash log and extract the seed
    try:
        with open(crash_log_path, 'r') as f:
            history = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing crash log {crash_log_path}: {e}")
        return

    seed = None
    seed_pattern = re.compile(r"Seed for this run: (\S+)")
    for item in history:
        match = seed_pattern.match(item)
        if match:
            seed = match.group(1)
            break
    
    if not seed:
        print(f"Error: Could not find seed value in {crash_log_path}")
        return

    # 3. Read the template test content
    with open(template_path, 'r') as f:
        template_content = f.read()

    # 4. Replace the random seed generation with the hardcoded seed
    modified_content = re.sub(
        r"seed_value = time\.time\("",
        f"seed_value = {seed}",
        template_content
    )

    # 5. Generate the new test file
    base_name = os.path.basename(crash_log_path)
    # e.g., crash_20231211_103000_code1.json -> test_repro_20231211_103000_code1.py
    new_filename = "test_repro_" + base_name.replace('crash_', '').replace('.json', '.py')
    output_path = os.path.join(repro_dir, new_filename)

    with open(output_path, 'w') as f:
        f.write(modified_content)

    print(f"Successfully created reproducible test case:\n{output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Create a reproducible test case from a chaos monkey crash log."
    )
    parser.add_argument(
        "crash_log",
        type=str,
        help="Path to the crash_...json file from the 'crashes' directory."
    )
    args = parser.parse_args()
    
    create_repro_test(args.crash_log)

if __name__ == "__main__":
    main()
