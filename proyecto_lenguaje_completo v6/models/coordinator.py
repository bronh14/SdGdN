from config.database import get_connection


class Coordinator:
    def __init__(
        self,
        id=None,
        user_id=None,
        carrera=None,
        fecha_ingreso=None,
    ):
        self.id = id
        self.user_id = user_id
        self.carrera = carrera
        self.fecha_ingreso = fecha_ingreso

    @classmethod
    def get_all(cls):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id_usuario, u.cedula, u.nombre, u.apellido, c.carrera, c.fecha_ingreso
            FROM usuarios u
            JOIN coordinadores c ON u.id_usuario = c.id_usuario
            WHERE u.rol = ?
        """,
            ("coordinacion",),
        )
        coordinators = cursor.fetchall()
        conn.close()
        return coordinators

    @classmethod
    def get_by_id(cls, coordinator_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id_usuario, u.cedula, u.nombre, u.apellido, c.carrera, c.fecha_ingreso
            FROM usuarios u
            JOIN coordinadores c ON u.id_usuario = c.id_usuario
            WHERE u.rol = ? AND u.id_usuario = ?
        """,
            ("coordinacion", coordinator_id),
        )
        coordinator_data = cursor.fetchone()
        conn.close()

        if coordinator_data:
            return Coordinator(
                id=coordinator_data[0],
                user_id=coordinator_data[0],
                carrera=coordinator_data[4],
                fecha_ingreso=coordinator_data[5],
            )
        return None

    @classmethod
    def create(cls, cedula, nombre, apellido, carrera, fecha_ingreso, **kwargs):
        conn = get_connection()
        cursor = conn.cursor()
        # Crear usuario
        cursor.execute(
            "INSERT INTO usuarios (cedula, nombre, apellido, contraseña_hash, rol) VALUES (?, ?, ?, ?, ?)",
            (
                cedula,
                nombre,
                apellido,
                kwargs.get("contraseña_hash", ""),
                "coordinacion",
            ),
        )
        user_id = cursor.lastrowid
        # Crear coordinador
        cursor.execute(
            "INSERT INTO coordinadores (id_usuario, carrera, fecha_ingreso) VALUES (?, ?, ?)",
            (user_id, carrera, fecha_ingreso),
        )
        conn.commit()
        conn.close()
        return True

    @classmethod
    def update(cls, coordinator_id, carrera=None, fecha_ingreso=None, **kwargs):
        conn = get_connection()
        cursor = conn.cursor()
        fields = []
        values = []
        if carrera is not None:
            fields.append("carrera = ?")
            values.append(carrera)
        if fecha_ingreso is not None:
            fields.append("fecha_ingreso = ?")
            values.append(fecha_ingreso)
        if not fields:
            conn.close()
            return False
        values.append(coordinator_id)
        sql = "UPDATE coordinadores SET " + ", ".join(fields) + " WHERE id_usuario = ?"
        cursor.execute(sql, tuple(values))
        conn.commit()
        conn.close()
        return True

    @classmethod
    def delete(cls, coordinator_id):
        conn = get_connection()
        cursor = conn.cursor()
        # Elimina primero de coordinadores, luego de usuarios
        cursor.execute(
            "DELETE FROM coordinadores WHERE id_usuario = ?", (coordinator_id,)
        )
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (coordinator_id,))
        conn.commit()
        conn.close()
        return True
