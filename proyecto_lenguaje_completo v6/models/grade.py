from config.database import get_db_connection, execute_with_retry
from datetime import datetime


class Grade:
    def __init__(
        self,
        id=None,
        inscripcion_id=None,
        tipo_evaluacion=None,
        valor_nota=None,
        fecha_evaluacion=None,
        comentarios=None,
    ):
        self.id = id
        self.inscripcion_id = inscripcion_id
        self.tipo_evaluacion = tipo_evaluacion
        self.valor_nota = valor_nota
        self.fecha_evaluacion = fecha_evaluacion
        self.comentarios = comentarios

    @staticmethod
    def create(
        inscripcion_id,
        tipo_evaluacion,
        valor_nota,
        fecha_evaluacion=None,
        comentarios=None,
    ):
        """Crea una nueva calificación en la base de datos."""

        def _create():
            with get_db_connection() as conn:
                cursor = conn.cursor()

                if not fecha_evaluacion:
                    fecha_evaluacion = datetime.now().strftime("%Y-%m-%d")

                cursor.execute(
                    """
                INSERT INTO calificaciones (id_inscripcion, tipo_evaluacion, valor_nota, fecha_evaluacion, comentarios)
                VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        inscripcion_id,
                        tipo_evaluacion,
                        valor_nota,
                        fecha_evaluacion,
                        comentarios,
                    ),
                )

                grade_id = cursor.lastrowid
                conn.commit()
                return Grade(
                    id=grade_id,
                    inscripcion_id=inscripcion_id,
                    tipo_evaluacion=tipo_evaluacion,
                    valor_nota=valor_nota,
                    fecha_evaluacion=fecha_evaluacion,
                    comentarios=comentarios,
                )

        return execute_with_retry(_create)

    @staticmethod
    def get_by_id(grade_id):
        """Obtiene una calificación por su ID."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_calificacion, id_inscripcion, tipo_evaluacion, valor_nota, fecha_evaluacion, comentarios
                FROM calificaciones
                WHERE id_calificacion = ?
                """,
                    (grade_id,),
                )
                grade_data = cursor.fetchone()
                if grade_data:
                    return Grade(
                        id=grade_data[0],
                        inscripcion_id=grade_data[1],
                        tipo_evaluacion=grade_data[2],
                        valor_nota=grade_data[3],
                        fecha_evaluacion=grade_data[4],
                        comentarios=grade_data[5],
                    )
                return None

        return execute_with_retry(_get)

    @staticmethod
    def get_by_enrollment(enrollment_id):
        """Obtiene todas las calificaciones de una inscripción."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_calificacion, id_inscripcion, tipo_evaluacion, valor_nota, fecha_evaluacion, comentarios
                FROM calificaciones
                WHERE id_inscripcion = ?
                """,
                    (enrollment_id,),
                )
                grades = []
                for grade_data in cursor.fetchall():
                    grades.append(
                        Grade(
                            id=grade_data[0],
                            inscripcion_id=grade_data[1],
                            tipo_evaluacion=grade_data[2],
                            valor_nota=grade_data[3],
                            fecha_evaluacion=grade_data[4],
                            comentarios=grade_data[5],
                        )
                    )
                return grades

        return execute_with_retry(_get)

    @staticmethod
    def get_student_grades(student_id):
        """Obtiene todas las calificaciones de un estudiante."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT c.id_calificacion, m.nombre, c.tipo_evaluacion, c.valor_nota, c.fecha_evaluacion
        FROM calificaciones c
        JOIN inscripciones i ON c.id_inscripcion = i.id_inscripcion
        JOIN secciones s ON i.id_seccion = s.id_seccion
        JOIN materias m ON s.id_materia = m.id_materia
        WHERE i.id_estudiante = ?
        """,
            (student_id,),
        )

        grades = cursor.fetchall()
        conn.close()

        return grades

    def update(self, valor_nota=None, comentarios=None):
        """Actualiza los datos de la calificación."""

        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()

                if valor_nota:
                    self.valor_nota = valor_nota

                if comentarios:
                    self.comentarios = comentarios

                cursor.execute(
                    """
                UPDATE calificaciones
                SET valor_nota = ?, comentarios = ?
                WHERE id_calificacion = ?
                """,
                    (self.valor_nota, self.comentarios, self.id),
                )

                conn.commit()
                return self

        return execute_with_retry(_update)

    @staticmethod
    def save_or_update(inscripcion_id, tipo_evaluacion, valor_nota):
        """Crea o actualiza la nota de un corte para una inscripción."""

        def _save_or_update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Verificar si ya existe la nota
                cursor.execute(
                    """
                SELECT id_calificacion FROM calificaciones
                WHERE id_inscripcion = ? AND tipo_evaluacion = ?
                """,
                    (inscripcion_id, tipo_evaluacion),
                )
                row = cursor.fetchone()
                if row:
                    # Actualizar
                    cursor.execute(
                        """
                    UPDATE calificaciones
                    SET valor_nota = ?
                    WHERE id_calificacion = ?
                    """,
                        (valor_nota, row[0]),
                    )
                else:
                    # Insertar
                    cursor.execute(
                        """
                    INSERT INTO calificaciones (id_inscripcion, tipo_evaluacion, valor_nota, fecha_evaluacion)
                    VALUES (?, ?, ?, date('now'))
                    """,
                        (inscripcion_id, tipo_evaluacion, valor_nota),
                    )
                conn.commit()

        return execute_with_retry(_save_or_update)

    @staticmethod
    def get_by_inscripcion(inscripcion_id):
        """Devuelve una lista de objetos Grade para una inscripción."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_calificacion, id_inscripcion, tipo_evaluacion, valor_nota, fecha_evaluacion
                FROM calificaciones
                WHERE id_inscripcion = ?
                """,
                    (inscripcion_id,),
                )
                result = []
                for row in cursor.fetchall():
                    grade = Grade(
                        id=row[0],
                        inscripcion_id=row[1],
                        tipo_evaluacion=row[2],
                        valor_nota=row[3],
                        fecha_evaluacion=row[4],
                    )
                    result.append(grade)
                return result

        return execute_with_retry(_get)

    def delete(self):
        """Elimina la calificación de la base de datos."""

        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                DELETE FROM calificaciones
                WHERE id_calificacion = ?
                """,
                    (self.id,),
                )
                conn.commit()

        return execute_with_retry(_delete)
