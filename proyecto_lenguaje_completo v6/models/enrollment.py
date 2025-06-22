from config.database import get_connection
from datetime import datetime


class Enrollment:
    def __init__(
        self,
        id=None,
        estudiante_id=None,
        seccion_id=None,
        fecha_inscripcion=None,
        estado=None,
    ):
        self.id = id
        self.estudiante_id = estudiante_id
        self.seccion_id = seccion_id
        self.fecha_inscripcion = fecha_inscripcion
        self.estado = estado

    @staticmethod
    def create(estudiante_id, seccion_id, fecha_inscripcion=None, estado="activo"):
        """Crea una nueva inscripción en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()

        if not fecha_inscripcion:
            fecha_inscripcion = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
        INSERT INTO inscripciones (id_estudiante, id_seccion, fecha_inscripcion, estado)
        VALUES (?, ?, ?, ?)
        """,
            (estudiante_id, seccion_id, fecha_inscripcion, estado),
        )

        enrollment_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return Enrollment(
            id=enrollment_id,
            estudiante_id=estudiante_id,
            seccion_id=seccion_id,
            fecha_inscripcion=fecha_inscripcion,
            estado=estado,
        )

    @staticmethod
    def get_by_id(enrollment_id):
        """Obtiene una inscripción por su ID."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT id_inscripcion, id_estudiante, id_seccion, fecha_inscripcion, estado
        FROM inscripciones
        WHERE id_inscripcion = ?
        """,
            (enrollment_id,),
        )

        enrollment_data = cursor.fetchone()
        conn.close()

        if enrollment_data:
            return Enrollment(
                id=enrollment_data[0],
                estudiante_id=enrollment_data[1],
                seccion_id=enrollment_data[2],
                fecha_inscripcion=enrollment_data[3],
                estado=enrollment_data[4],
            )
        return None

    @staticmethod
    def get_by_student(student_id):
        """Obtiene todas las inscripciones de un estudiante."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT i.id_inscripcion, m.nombre, s.periodo,  s.aula, u.nombre || ' ' || u.apellido as profesor
        FROM inscripciones i
        JOIN secciones s ON i.id_seccion = s.id_seccion
        JOIN materias m ON s.id_materia = m.id_materia
        JOIN profesores p ON s.id_profesor = p.id_profesor
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE i.id_estudiante = ?
        """,
            (student_id,),
        )

        enrollments = cursor.fetchall()
        conn.close()

        return enrollments

    @staticmethod
    def get_by_section(section_id):
        """Obtiene todas las inscripciones de una sección."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT i.id_inscripcion, u.cedula, u.nombre, u.apellido, i.fecha_inscripcion, i.estado
        FROM inscripciones i
        JOIN estudiantes e ON i.id_estudiante = e.id_estudiante
        JOIN usuarios u ON e.id_usuario = u.id_usuario
        WHERE i.id_seccion = ?
        """,
            (section_id,),
        )

        enrollments = cursor.fetchall()
        conn.close()

        return enrollments

    def update(self, estado=None):
        """Actualiza los datos de la inscripción."""
        conn = get_connection()
        cursor = conn.cursor()

        if estado:
            self.estado = estado

        cursor.execute(
            """
        UPDATE inscripciones
        SET estado = ?
        WHERE id_inscripcion = ?
        """,
            (self.estado, self.id),
        )

        conn.commit()
        conn.close()

        return self

    @staticmethod
    def get_materias_cursadas(estudiante_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_materia, estado FROM materias_cursadas WHERE id_estudiante = ?",
            (estudiante_id,),
        )
        result = [{"id_materia": row[0], "estado": row[1]} for row in cursor.fetchall()]
        conn.close()
        return result

    @staticmethod
    def get_materias_inscritas(estudiante_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.id_materia FROM inscripciones i
            JOIN secciones s ON i.id_seccion = s.id_seccion
            JOIN materias m ON s.id_materia = m.id_materia
            WHERE i.id_estudiante = ? AND i.estado = 'activo'
            """,
            (estudiante_id,),
        )
        result = set(row[0] for row in cursor.fetchall())
        conn.close()
        return result

    def delete(self):
        """Elimina la inscripción de la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        DELETE FROM inscripciones
        WHERE id_inscripcion = ?
        """,
            (self.id,),
        )

        conn.commit()
        conn.close()
