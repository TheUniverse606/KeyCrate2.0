from cryptography.fernet import Fernet
import bcrypt
import base64
import os

class Encryption:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
        key_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'encryption.key')
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
            return key

    def encrypt_password(self, password: str) -> bytes:
        return self.fernet.encrypt(password.encode())

    def decrypt_password(self, encrypted_password: bytes) -> str:
        return self.fernet.decrypt(encrypted_password).decode()

    def hash_master_password(self, password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def verify_master_password(self, password: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(password.encode(), hashed)

    def generate_secure_password(self, length: int = 16) -> str:
        return base64.b64encode(os.urandom(length)).decode('utf-8')[:length]
