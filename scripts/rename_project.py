
import os
import re

def rename_project(root_dir):
    replacements = {
        "Scova": "Scova",
        "SCOVA": "SCOVA",
        "scova": "scova"
    }

    # Files to ignore
    ignore_dirs = {'.git', '.idea', '__pycache__', 'venv', 'env', '.DS_Store', 'build', '.agent', '.cursorrules'}
    ignore_files = {'.DS_Store'}

    # 1. Rename Files
    print(f"--- Renaming Files in {root_dir} ---")
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Filter directories in place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        
        for filename in filenames:
            if filename in ignore_files:
                continue
                
            old_path = os.path.join(dirpath, filename)
            
            # Check if filename needs renaming
            new_filename = filename
            for old_term, new_term in replacements.items():
                if old_term in new_filename:
                    new_filename = new_filename.replace(old_term, new_term)
            
            if new_filename != filename:
                new_path = os.path.join(dirpath, new_filename)
                print(f"Renaming file: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

    # 2. Replace Content
    print(f"\n--- Replacing Content in {root_dir} ---")
    for dirpath, dirnames, filenames in os.walk(root_dir):
         # Filter directories in place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        
        for filename in filenames:
            if filename in ignore_files:
                continue
            
            # Skip binary files/images just in case, focusing on likely text
            if filename.endswith(('.png', '.jpg', '.jpeg', '.parquet', '.pyc', '.git', '.ico', '.icns')):
                continue

            filepath = os.path.join(dirpath, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                for old_term, new_term in replacements.items():
                    new_content = new_content.replace(old_term, new_term)
                
                if new_content != content:
                    print(f"Modifying content in: {filepath}")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
            except UnicodeDecodeError:
                print(f"Skipping binary file (decode error): {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    rename_project(root)
