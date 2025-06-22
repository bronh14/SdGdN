import re


def validate_cedula(cedula):
    """Valida que la cédula tenga el formato correcto."""
    # Implementar según las reglas específicas del país
    return len(cedula) > 0


def validate_email(email):
    """Valida que el email tenga un formato correcto."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Valida que el teléfono tenga un formato correcto."""
    pattern = r"^\+?[0-9]{8,15}$"
    return re.match(pattern, phone) is not None


def validate_password_strength(password):
    # Valida que la  phone) is not None
    # Valida que la contraseña tenga una fortaleza adecuada
    # Verificar longitud mínima
    if len(password) < 8:
        return False

    # Verificar que contenga al menos una letra mayúscula
    if not re.search(r"[A-Z]", password):
        return False

    # Verificar que contenga al menos una letra minúscula
    if not re.search(r"[a-z]", password):
        return False

    # Verificar que contenga al menos un número
    if not re.search(r"[0-9]", password):
        return False

    return True
