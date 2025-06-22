from models.user import User
from models.professor import Professor
from models.student import Student
from datetime import datetime


class AuthController:
    def login(self, cedula, password):
        """Autentica un usuario con su cédula y contraseña."""
        # Validar campos
        if not all([cedula, password]):
            raise ValueError("Todos los campos son obligatorios")

        # Intentar autenticar
        return User.authenticate(cedula, password)

    def register(
        self, cedula, nombre, apellido, password, confirm_password, rol, carrera=None
    ):
        """Registra un nuevo usuario en el sistema."""
        # Validar campos
        if not all([cedula, nombre, apellido, password, confirm_password, rol]):
            raise ValueError("Todos los campos son obligatorios")

        if password != confirm_password:
            raise ValueError("Las contraseñas no coinciden")

        # Crear usuario
        user = User.create(cedula, nombre, apellido, password, rol)

        # Crear registro adicional según el rol
        if rol == "profesor":
            Professor.create(
                user.id, "Sin asignar", None, datetime.now().strftime("%Y-%m-%d")
            )
        elif rol == "alumno":
            Student.create(
                user.id,
                carrera or "Sin asignar",
                None,
                datetime.now().strftime("%Y-%m-%d"),
            )

        return user
