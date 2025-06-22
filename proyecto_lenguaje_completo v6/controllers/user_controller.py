from models.user import User


class UserController:
    def get_all(self):
        """Obtiene todos los usuarios."""
        return User.get_all()

    def get_by_id(self, user_id):
        """Obtiene un usuario por su ID."""
        return User.get_by_id(user_id)

    def update(self, user_id, nombre=None, apellido=None, password=None):
        """Actualiza los datos de un usuario."""
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        return user.update(nombre, apellido, password)

    def delete(self, user_id):
        """Elimina un usuario."""
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        user.delete()
