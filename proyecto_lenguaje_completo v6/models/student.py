from config.database import get_db_connection, execute_with_retry


class Student:
    def __init__(
        self, id=None, user_id=None, carrera=None, semestre=None, fecha_ingreso=None
    ):
        self.id = id
        self.user_id = user_id
        self.carrera = carrera
        self.semestre = semestre
        self.fecha_ingreso = fecha_ingreso

    @staticmethod
    def create(user_id, carrera, semestre, fecha_ingreso):
        """Crea un nuevo registro de estudiante en la base de datos."""

        def _create():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                INSERT INTO estudiantes (id_usuario, carrera, semestre, fecha_ingreso)
                VALUES (?, ?, ?, ?)
                """,
                    (user_id, carrera, semestre, fecha_ingreso),
                )
                student_id = cursor.lastrowid
                conn.commit()
                return Student(
                    id=student_id,
                    user_id=user_id,
                    carrera=carrera,
                    semestre=semestre,
                    fecha_ingreso=fecha_ingreso,
                )

        return execute_with_retry(_create)

    @staticmethod
    def get_by_user_id(user_id):
        """Obtiene un estudiante por su ID de usuario."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_estudiante, id_usuario, carrera, semestre, fecha_ingreso
                FROM estudiantes
                WHERE id_usuario = ?
                """,
                    (user_id,),
                )
                student_data = cursor.fetchone()
                if student_data:
                    return Student(
                        id=student_data[0],
                        user_id=student_data[1],
                        carrera=student_data[2],
                        semestre=student_data[3],
                        fecha_ingreso=student_data[4],
                    )
                return None

        return execute_with_retry(_get)

    @staticmethod
    def get_by_id(student_id):
        """Obtiene un estudiante por su ID."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_estudiante, id_usuario, carrera, semestre, fecha_ingreso
                FROM estudiantes
                WHERE id_estudiante = ?
                """,
                    (student_id,),
                )
                student_data = cursor.fetchone()
                if student_data:
                    return Student(
                        id=student_data[0],
                        user_id=student_data[1],
                        carrera=student_data[2],
                        semestre=student_data[3],
                        fecha_ingreso=student_data[4],
                    )
                return None

        return execute_with_retry(_get)

    @staticmethod
    def get_all():
        """Obtiene todos los estudiantes con información de usuario."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT e.id_estudiante, u.cedula, u.nombre, u.apellido, 
                       e.carrera, e.semestre, e.fecha_ingreso
                FROM estudiantes e
                JOIN usuarios u ON e.id_usuario = u.id_usuario
                """
                )
                students = cursor.fetchall()
                return students

        return execute_with_retry(_get)

    def update(self, carrera=None, semestre=None):
        """Actualiza los datos del estudiante."""

        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if carrera:
                    self.carrera = carrera
                if semestre:
                    self.semestre = semestre
                cursor.execute(
                    """
                UPDATE estudiantes
                SET carrera = ?, semestre = ?
                WHERE id_estudiante = ?
                """,
                    (self.carrera, self.semestre, self.id),
                )
                conn.commit()
                return self

        return execute_with_retry(_update)

    @classmethod
    def delete(cls, student_id):
        """Elimina el estudiante y su usuario de la base de datos."""

        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Obtener el id_usuario asociado a este estudiante
                cursor.execute(
                    "SELECT id_usuario FROM estudiantes WHERE id_estudiante = ?",
                    (student_id,),
                )
                row = cursor.fetchone()
                if row:
                    user_id = row[0]
                    # Elimina primero de estudiantes, luego de usuarios
                    cursor.execute(
                        "DELETE FROM estudiantes WHERE id_estudiante = ?", (student_id,)
                    )
                    cursor.execute(
                        "DELETE FROM usuarios WHERE id_usuario = ?", (user_id,)
                    )
                    conn.commit()
                return True

        return execute_with_retry(_delete)
