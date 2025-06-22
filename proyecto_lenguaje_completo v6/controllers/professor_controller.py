from models.professor import Professor


class ProfessorController:
    def get_all(self):
        """Obtiene todos los profesores."""
        return Professor.get_all()

    def get_by_id(self, professor_id):
        """Obtiene un profesor por su ID."""
        return Professor.get_by_id(professor_id)

    def get_id_by_cedula(self, cedula):
        """Obtiene el id_usuario de un profesor por su cédula."""
        professors = self.get_all()
        for p in professors:
            if str(p[1]) == str(cedula):  # p[1] es cedula
                return p[0]  # p[0] es id_usuario
        return None

    def create(self, cedula, nombre, apellido, carrera, fecha_contratacion):
        """Crea un nuevo profesor."""
        import hashlib

        password = "profesor123"
        contraseña_hash = hashlib.sha256(password.encode()).hexdigest()
        return Professor.create(
            cedula,
            nombre,
            apellido,
            carrera,
            fecha_contratacion,
            contraseña_hash,
        )

    def update(
        self,
        professor_id,
        cedula,
        nombre,
        apellido,
        carrera,
        fecha_contratacion,
    ):
        """Actualiza los datos de un profesor."""
        from models.user import User

        professor = Professor.get_by_id(professor_id)
        if not professor:
            raise ValueError("Profesor no encontrado")
        user = User.get_by_id(professor.user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        user.update(cedula=cedula, nombre=nombre, apellido=apellido)

        return Professor.update(
            professor_id,
            carrera=carrera,
            fecha_contratacion=fecha_contratacion,
        )

    def delete(self, professor_id):
        """Elimina un profesor y su usuario asociado."""
        professor = Professor.get_by_id(professor_id)
        if not professor:
            raise ValueError("Profesor no encontrado")
        return Professor.delete(professor_id)
