# rag-system/utils/file_utils.py

import os


def ensure_dir(path: str):
    """
    Ensure that a directory exists. 
    If it does not exist, create it.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"[file_utils] Created directory: {path}")
    else:
        print(f"[file_utils] Directory already exists: {path}")


def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    """
    return os.path.isfile(path)


def dir_exists(path: str) -> bool:
    """
    Check if a directory exists.
    """
    return os.path.isdir(path)
