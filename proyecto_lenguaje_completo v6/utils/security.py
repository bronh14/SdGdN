import hashlib
import random
import string


def hash_password(password):
    """Encripta una contraseña usando SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verifica si una contraseña coincide con su hash."""
    return hash_password(password) == password_hash


def generate_random_password(length=8):
    """Genera una contraseña aleatoria."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for i in range(length))
