from models.coordinator import Coordinator


class CoordinatorController:
    def get_all(self):
        """Obtiene todos los coordinadores."""
        return Coordinator.get_all()

    def get_by_id(self, coordinator_id):
        """Obtiene un coordinador por su ID."""
        return Coordinator.get_by_id(coordinator_id)

    def get_id_by_cedula(self, cedula):
        """Obtiene el id_usuario de un coordinador por su cédula."""
        coordinators = self.get_all()
        for c in coordinators:
            if str(c[1]) == str(cedula):  # c[1] es cedula
                return c[0]  # c[0] es id_usuario
        return None

    def create(self, cedula, nombre, apellido, carrera, fecha_ingreso):
        """Crea un nuevo coordinador."""
        import hashlib

        password = "coordinador123"
        contraseña_hash = hashlib.sha256(password.encode()).hexdigest()
        return Coordinator.create(
            cedula,
            nombre,
            apellido,
            carrera,
            fecha_ingreso,
            contraseña_hash=contraseña_hash,
        )

    def update(self, coordinator_id, cedula, nombre, apellido, carrera, fecha_ingreso):
        """Actualiza los datos de un coordinador."""
        from models.user import User

        coordinator = Coordinator.get_by_id(coordinator_id)
        if not coordinator:
            raise ValueError("Coordinador no encontrado")
        user = User.get_by_id(coordinator.user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        user.update(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
        )

        return Coordinator.update(
            coordinator_id, carrera=carrera, fecha_ingreso=fecha_ingreso
        )

    def delete(self, coordinator_id):
        """Elimina un coordinador."""
        coordinator = Coordinator.get_by_id(coordinator_id)
        if not coordinator:
            raise ValueError("Coordinador no encontrado")
        return Coordinator.delete(coordinator_id)
