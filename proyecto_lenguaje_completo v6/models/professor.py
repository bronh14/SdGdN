from config.database import get_db_connection, execute_with_retry


class Professor:
    def __init__(
        self,
        id=None,
        user_id=None,
        carrera=None,
        fecha_contratacion=None,
    ):
        self.id = id
        self.user_id = user_id
        self.carrera = carrera
        self.fecha_contratacion = fecha_contratacion

    @classmethod
    def create(
        cls,
        cedula,
        nombre,
        apellido,
        carrera,
        fecha_contratacion,
        contraseña_hash,
    ):
        """Crea un nuevo usuario y profesor en la base de datos."""

        def _create():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Crear usuario
                cursor.execute(
                    "INSERT INTO usuarios (cedula, nombre, apellido, contraseña_hash, rol) VALUES (?, ?, ?, ?, ?)",
                    (cedula, nombre, apellido, contraseña_hash, "profesor"),
                )
                user_id = cursor.lastrowid
                # Crear profesor
                cursor.execute(
                    "INSERT INTO profesores (id_usuario, carrera,  fecha_contratacion) VALUES (?, ?, ?)",
                    (user_id, carrera, fecha_contratacion),
                )
                conn.commit()
            return True

        return execute_with_retry(_create)

    @staticmethod
    def get_by_user_id(user_id):
        from config.database import get_db_connection

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profesores WHERE id_usuario = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return Professor(*row)
            return None
        # """Obtiene un profesor por su ID de usuario."""
        # conn = get_connection()
        # cursor = conn.cursor()

        # cursor.execute(
        #     """
        # SELECT id_profesor, id_usuario, carrera, fecha_contratacion
        # FROM profesores
        # WHERE id_usuario = ?
        # """,
        #     (user_id,),
        # )

        # professor_data = cursor.fetchone()
        # conn.close()

        # if professor_data:
        #     return Professor(
        #         id=professor_data[0],
        #         user_id=professor_data[1],
        #         carrera=professor_data[2],
        #         fecha_contratacion=professor_data[3],
        #     )
        # return None

    @staticmethod
    def get_by_id(professor_id):
        """Obtiene un profesor por su ID."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_profesor, id_usuario, carrera, fecha_contratacion
                FROM profesores
                WHERE id_profesor = ?
                """,
                    (professor_id,),
                )
                professor_data = cursor.fetchone()
                if professor_data:
                    return Professor(
                        id=professor_data[0],
                        user_id=professor_data[1],
                        carrera=professor_data[2],
                        fecha_contratacion=professor_data[3],
                    )
                return None

        return execute_with_retry(_get)

    @staticmethod
    def get_all():
        """Obtiene todos los profesores con información de usuario."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT p.id_profesor, u.cedula, u.nombre, u.apellido, 
                       p.carrera,  p.fecha_contratacion
                FROM profesores p
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                """
                )
                professors = cursor.fetchall()
                return professors

        return execute_with_retry(_get)

    @classmethod
    def update(cls, professor_id, carrera=None, fecha_contratacion=None):
        """Actualiza los datos del profesor."""

        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                fields = []
                values = []
                if carrera is not None:
                    fields.append("carrera = ?")
                    values.append(carrera)
                if fecha_contratacion is not None:
                    fields.append("fecha_contratacion = ?")
                    values.append(fecha_contratacion)
                if not fields:
                    return False
                values.append(professor_id)
                sql = (
                    "UPDATE profesores SET "
                    + ", ".join(fields)
                    + " WHERE id_profesor = ?"
                )
                cursor.execute(sql, tuple(values))
                conn.commit()
                return True

        return execute_with_retry(_update)

    def delete(self):
        """Elimina el profesor de la base de datos."""

        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                DELETE FROM profesores
                WHERE id_profesor = ?
                """,
                    (self.id,),
                )
                conn.commit()

        return execute_with_retry(_delete)

    @classmethod
    def delete(cls, professor_id):
        """Elimina el profesor y su usuario asociado de la base de datos."""

        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Obtener el id_usuario asociado a este profesor
                cursor.execute(
                    "SELECT id_usuario FROM profesores WHERE id_profesor = ?",
                    (professor_id,),
                )
                row = cursor.fetchone()
                if row:
                    user_id = row[0]
                    # Elimina primero de profesores, luego de usuarios
                    cursor.execute(
                        "DELETE FROM profesores WHERE id_profesor = ?", (professor_id,)
                    )
                    cursor.execute(
                        "DELETE FROM usuarios WHERE id_usuario = ?", (user_id,)
                    )
                    conn.commit()
            return True

        return execute_with_retry(_delete)
