import sqlite3
import hashlib
from config.database import get_db_connection, execute_with_retry


class User:
    def __init__(self, id=None, cedula=None, nombre=None, apellido=None, rol=None):
        self.id = id
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.rol = rol

    @staticmethod
    def authenticate(cedula, password):
        """Autentica un usuario con su cédula y contraseña."""

        def _auth():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute(
                    """
                SELECT id_usuario, cedula, nombre, apellido, rol
                FROM usuarios
                WHERE cedula = ? AND contraseña_hash = ?
                """,
                    (cedula, password_hash),
                )
                user_data = cursor.fetchone()
                if user_data:
                    return User(
                        id=user_data[0],
                        cedula=user_data[1],
                        nombre=user_data[2],
                        apellido=user_data[3],
                        rol=user_data[4],
                    )
                return None

        return execute_with_retry(_auth)

    @staticmethod
    def create(cedula, nombre, apellido, password, rol):
        """Crea un nuevo usuario en la base de datos."""

        def _create():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute(
                    """
                INSERT INTO usuarios (cedula, nombre, apellido, contraseña_hash, rol)
                VALUES (?, ?, ?, ?, ?)
                """,
                    (cedula, nombre, apellido, password_hash, rol),
                )
                user_id = cursor.lastrowid
                conn.commit()
                return User(
                    id=user_id, cedula=cedula, nombre=nombre, apellido=apellido, rol=rol
                )

        try:
            return execute_with_retry(_create)
        except sqlite3.IntegrityError:
            raise ValueError("La cédula ya está registrada en el sistema")
        except Exception as e:
            raise e

    @staticmethod
    def get_by_id(user_id):
        """Obtiene un usuario por su ID."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_usuario, cedula, nombre, apellido, rol
                FROM usuarios
                WHERE id_usuario = ?
                """,
                    (user_id,),
                )
                user_data = cursor.fetchone()
                if user_data:
                    return User(
                        id=user_data[0],
                        cedula=user_data[1],
                        nombre=user_data[2],
                        apellido=user_data[3],
                        rol=user_data[4],
                    )
                return None

        return execute_with_retry(_get)

    @staticmethod
    def get_all():
        """Obtiene todos los usuarios."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_usuario, cedula, nombre, apellido, rol
                FROM usuarios
                """
                )
                users = []
                for user_data in cursor.fetchall():
                    users.append(
                        User(
                            id=user_data[0],
                            cedula=user_data[1],
                            nombre=user_data[2],
                            apellido=user_data[3],
                            rol=user_data[4],
                        )
                    )
                return users

        return execute_with_retry(_get)

    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombre} {self.apellido}"

    def update(self, cedula=None, nombre=None, apellido=None):
        """Actualiza la cédula, nombre y apellido del usuario."""

        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if cedula:
                    self.cedula = cedula
                if nombre:
                    self.nombre = nombre
                if apellido:
                    self.apellido = apellido
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET cedula = ?, nombre = ?, apellido = ?
                    WHERE id_usuario = ?
                    """,
                    (self.cedula, self.nombre, self.apellido, self.id),
                )
                conn.commit()
                return self

        return execute_with_retry(_update)

    def delete(self):
        """Elimina el usuario de la base de datos."""

        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                DELETE FROM usuarios
                WHERE id_usuario = ?
                """,
                    (self.id,),
                )
                conn.commit()

        return execute_with_retry(_delete)
