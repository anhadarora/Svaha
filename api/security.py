import os
from cryptography.fernet import Fernet
import logging

logging.basicConfig(level=logging.INFO)

KEY_FILE = os.path.join(os.path.dirname(
    __file__), "..", "generated_data", "encryption.key")


def generate_key():
    """
    Generates a key and save it into a file
    """
    logging.info("Generating new encryption key.")
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key


def load_key():
    """
    Load the previously generated key
    """
    if not os.path.exists(KEY_FILE):
        return generate_key()
    logging.info("Loading existing encryption key.")
    return open(KEY_FILE, "rb").read()


def encrypt_data(data, key):
    """
    Encrypts data using the provided key
    """
    fernet = Fernet(key)
    return fernet.encrypt(data)


def decrypt_data(encrypted_data, key):
    """
    Decrypts data using the provided key
    """
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)