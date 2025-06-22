from config.database import get_db_connection, execute_with_retry
from models.section import Section


class SectionController:
    def get_all(self):
        """Obtiene todas las secciones"""

        def _get_all():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        s.id_seccion,
                        m.codigo,
                        m.nombre,
                        s.numero_seccion,
                        COALESCE(u.nombre || ' ' || u.apellido, 'Por asignar') as profesor,
                        COALESCE(s.aula, 'Por asignar') as aula,
                        s.capacidad,
                        s.estado,
                        s.periodo
                    FROM secciones s
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN profesores p ON s.id_profesor = p.id_profesor
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    ORDER BY m.codigo, s.numero_seccion
                """
                )
                return cursor.fetchall()

        return execute_with_retry(_get_all)

    def get_section(self, section_id):
        """Obtiene una sección específica"""

        def _get_section():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        s.*,
                        m.nombre as nombre_materia,
                        COALESCE(u.nombre || ' ' || u.apellido, 'Por asignar') as nombre_profesor
                    FROM secciones s
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN profesores p ON s.id_profesor = p.id_profesor
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE s.id_seccion = ?
                """,
                    (section_id,),
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id_seccion": row[0],
                        "id_materia": row[1],
                        "numero_seccion": row[2],
                        "id_profesor": row[3],
                        "periodo": row[4],
                        "aula": row[5],
                        "capacidad": row[6],
                        "estado": row[7],
                        "nombre_materia": row[8],
                        "nombre_profesor": row[9],
                    }
                return None

        return execute_with_retry(_get_section)

    def create_section(
        self, materia_id, numero_seccion, id_profesor, periodo, aula, capacidad, estado
    ):
        """Crea una nueva sección"""

        def _create_section():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO secciones (
                        id_materia, numero_seccion, id_profesor, periodo, 
                        aula, capacidad, estado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        materia_id,
                        numero_seccion,
                        id_profesor,
                        periodo,
                        aula,
                        capacidad,
                        estado,
                    ),
                )
                conn.commit()

        execute_with_retry(_create_section)

    def update_section(
        self,
        section_id,
        materia_id,
        numero_seccion,
        id_profesor,
        periodo,
        aula,
        capacidad,
        estado,
    ):
        """Actualiza una sección existente"""

        def _update_section():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE secciones 
                    SET id_materia = ?, numero_seccion = ?, id_profesor = ?, 
                        periodo = ?, aula = ?, capacidad = ?, estado = ?
                    WHERE id_seccion = ?
                """,
                    (
                        materia_id,
                        numero_seccion,
                        id_profesor,
                        periodo,
                        aula,
                        capacidad,
                        estado,
                        section_id,
                    ),
                )
                conn.commit()

        execute_with_retry(_update_section)

    def delete_section(self, section_id):
        """Elimina una sección"""

        def _delete_section():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM secciones WHERE id_seccion = ?", (section_id,)
                )
                conn.commit()

        execute_with_retry(_delete_section)

    def get_materias(self):
        """Obtiene la lista de materias"""

        def _get_materias():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id_materia, nombre FROM materias ORDER BY nombre"
                )
                return cursor.fetchall()

        return execute_with_retry(_get_materias)

    def get_profesores(self):
        """Obtiene la lista de profesores"""

        def _get_profesores():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT p.id_profesor, u.nombre || ' ' || u.apellido as nombre
                    FROM profesores p
                    JOIN usuarios u ON p.id_usuario = u.id_usuario
                    ORDER BY nombre
                """
                )
                return cursor.fetchall()

        return execute_with_retry(_get_profesores)

    def get_by_id(self, section_id):
        """Obtiene una sección específica por su ID."""
        return self.get_section(section_id)

    def get_by_professor(self, professor_id):
        """Obtiene todas las secciones de un profesor."""
        return Section.get_by_professor(professor_id)

    def exists(self, materia_id, numero_seccion, periodo, exclude_id=None):
        from config.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) 
            FROM secciones 
            WHERE id_materia = ? AND numero_seccion = ? AND periodo = ?
        """
        params = (materia_id, numero_seccion, periodo)
        if exclude_id:
            query += " AND id_seccion != ?"
            params += (exclude_id,)
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def delete(self, section_id):
        """Elimina una sección por su ID"""
        from models.section import Section

        return Section.delete(section_id)
