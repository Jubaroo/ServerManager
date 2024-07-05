import os

from cryptography.fernet import Fernet


class SecureStorage:
    def __init__(self, key_file="key.key"):
        self.key_file = key_file
        if not os.path.exists(self.key_file):
            self.generate_key()
        self.key = self.load_key()

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        return open(self.key_file, "rb").read()

    def encrypt_data(self, data):
        f = Fernet(self.key)
        return f.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        f = Fernet(self.key)
        return f.decrypt(encrypted_data).decode()


# Usage example
storage = SecureStorage()
encrypted_data = storage.encrypt_data("Sensitive information")
print("Encrypted:", encrypted_data)
decrypted_data = storage.decrypt_data(encrypted_data)
print("Decrypted:", decrypted_data)
