import os
import shutil
import argparse
from pathlib import Path
import sys

# List of protected system directories in macOS
PROTECTED_PATHS = [
    "/", "/Applications", "/System", "/Volumes", "/cores", "/etc", "/opt", "/sbin", "/usr",
    "/Library", "/Users", "/bin", "/dev", "/home", "/private", "/tmp", "/var"
]

def is_protected_path(path):
    """Check if the given path is a protected macOS system directory."""
    path = str(Path(path).resolve())  # Resolve absolute path
    return any([path == protected or path == f"{protected}/" for protected in PROTECTED_PATHS])

def extract_timestamp(path):
    """Extracts timestamp from the directory path."""
    try:
        return int(path.name.replace("_", ""))
    except ValueError:
        return None

def restructure_logs(root_dir):
    """Restructure log directories safely."""
    if is_protected_path(root_dir):
        print(f"ERROR: The specified path '{root_dir}' is a protected system directory! Aborting.")
        sys.exit(1)

    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"ERROR: The directory '{root_dir}' does not exist.")
        sys.exit(1)

    all_timestamps = []
    
    # Collect all timestamps from the directory structure
    for pb_file in root_path.rglob("*.pb"):
        timestamp = extract_timestamp(pb_file.parent)
        if timestamp:
            all_timestamps.append(timestamp)
            
    if not all_timestamps:
        print("No timestamps found in the directory.")
        return
    
    min_timestamp = min(all_timestamps)
    max_timestamp = max(all_timestamps)
    
    # Define new directory path
    new_parent_folder = f"{str(min_timestamp)[:4]}-{str(min_timestamp)[4:6]}[{str(min_timestamp)[6:]}-{str(max_timestamp)[6:]}]"
    new_root = root_path / new_parent_folder
    new_profile_path = new_root / "plugins" / "profile"
    new_profile_path.mkdir(parents=True, exist_ok=True)
    
    for pb_file in root_path.rglob("*.pb"):
        parts = pb_file.parts
        if len(parts) < 8:
            print(f"Skipping malformed path: {pb_file}")
            continue
        
        data, cache, device, batch, file_name = parts[-8], parts[-7], parts[-6], parts[-5], parts[-1]
        new_folder_name = f"{data}-{cache}-{device}-{batch}"
        new_folder_path = new_profile_path / new_folder_name
        new_folder_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists before copying
        shutil.copy2(pb_file, new_folder_path / file_name)

    print(f"Logs restructured and saved to: {new_root}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restructure log directories safely on macOS.")
    parser.add_argument("root_dir", type=str, help="Path to the root log directory")
    args = parser.parse_args()
    restructure_logs(args.root_dir)
