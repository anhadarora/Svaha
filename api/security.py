from cryptography.fernet import Fernet
import os

KEY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'encryption.key')

def generate_key():
    """
    Generates a new encryption key and saves it to the KEY_FILE.
    """
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    """
    Loads the encryption key from the KEY_FILE.
    If the key file does not exist, it generates a new key.
    """
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """
    Encrypts data using the provided key.
    """
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypts data using the provided key.
    """
    f = Fernet(key)
    return f.decrypt(encrypted_data)
