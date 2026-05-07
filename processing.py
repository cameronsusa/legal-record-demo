import hashlib

def generate_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

def detect_duplicate(hash_value, existing_hashes):
    return hash_value in existing_hashes
