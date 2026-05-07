import hashlib
from datetime import datetime

def generate_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

def process_uploaded_files(uploaded_files):
    chronology_records = []
    duplicate_records = []

    seen_hashes = set()

    for file in uploaded_files:
        file_bytes = file.read()

        file_hash = generate_file_hash(file_bytes)

        record = {
            "filename": file.name,
            "hash": file_hash,
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Duplicate Detection
        if file_hash in seen_hashes:
            duplicate_records.append(record)
        else:
            seen_hashes.add(file_hash)
            chronology_records.append(record)

    return chronology_records, duplicate_records
