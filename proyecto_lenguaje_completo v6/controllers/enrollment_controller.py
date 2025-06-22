from models.enrollment import Enrollment
from datetime import datetime
from models.section import Section
from config.database import get_connection


class EnrollmentController:

    def get_materias_cursadas(self, estudiante_id):
        return Enrollment.get_materias_cursadas(estudiante_id)

    def get_materias_inscritas(self, estudiante_id):
        return Enrollment.get_materias_inscritas(estudiante_id)

    def get_by_id(self, enrollment_id):
        """Obtiene una inscripción por su ID."""
        return Enrollment.get_by_id(enrollment_id)

    def get_by_student(self, student_id):
        """Obtiene todas las inscripciones de un estudiante."""
        return Enrollment.get_by_student(student_id)

    def get_by_section(self, section_id):
        """Obtiene todas las inscripciones de una sección."""
        return Enrollment.get_by_section(section_id)

    @staticmethod
    def create(estudiante_id, seccion_id, fecha_inscripcion=None, estado="activo"):
        """Crea una nueva inscripción en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener id_materia de la sección
        cursor.execute(
            "SELECT id_materia FROM secciones WHERE id_seccion = ?", (seccion_id,)
        )
        row = cursor.fetchone()
        if row:
            id_materia = row[0]
            # Verificar si la materia ya fue aprobada
            cursor.execute(
                "SELECT 1 FROM materias_cursadas WHERE id_estudiante = ? AND id_materia = ? AND estado = 'APROBÓ'",
                (estudiante_id, id_materia)
            )
            if cursor.fetchone():
                conn.close()
                raise Exception("No puedes inscribir una materia ya aprobada.")

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

    def update_status(self, enrollment_id, estado):
        """Actualiza el estado de una inscripción."""
        enrollment = Enrollment.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Inscripción no encontrada")

        return enrollment.update(estado)

    def delete(self, enrollment_id):
        """Elimina una inscripción."""
        enrollment = Enrollment.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Inscripción no encontrada")

        enrollment.delete()

    def get_sections_by_materia_and_periodo(self, materia_id, periodo):
        """Obtiene las secciones disponibles para una materia y período dados."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_seccion, numero_seccion 
                FROM secciones 
                WHERE id_materia = ? AND periodo = ? AND estado = 'activa'
                ORDER BY numero_seccion
            """,
                (materia_id, periodo),
            )
            return [(int(row[0]), row[1]) for row in cursor.fetchall()]
