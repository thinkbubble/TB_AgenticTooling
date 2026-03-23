# helper.py just contains a bunch of functions
# that can be used in any program, they are program
# and/or environment agnostic.

from cryptography.fernet import Fernet
from typing import Any, List, Dict
from pathlib import Path
import hashlib
import json
import csv
import os



# 1. Load JSON
def load_json(file_path: str) -> Any:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# 2. Save JSON
def save_json(data: Any, file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


# 3. Load CSV
def load_csv(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


# 4. Save CSV
def save_csv(data: List[Dict[str, Any]], file_path: str) -> None:
    if not data:
        return
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


# 5. Ensure Directory Exists
def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


# 6. List Files in Directory
def list_files(directory: str, extension: str = None) -> List[str]:
    files = []
    for file in Path(directory).iterdir():
        if file.is_file():
            if extension:
                if file.suffix == extension:
                    files.append(str(file))
            else:
                files.append(str(file))
    return files


# 7. Read Text File
def read_text(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# 8. Write Text File
def write_text(file_path: str, content: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


# 9. Hash (SHA256)
def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


# 10. Encrypt / Decrypt (Fernet symmetric encryption)
def generate_key() -> bytes:
    return Fernet.generate_key()


def encrypt_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())


def decrypt_data(token: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token).decode()