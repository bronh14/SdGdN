from config.database import get_db_connection, execute_with_retry


class Section:

    def __init__(
        self,
        id=None,
        materia_id=None,
        profesor_id=None,
        numero_seccion=None,
        periodo=None,
        aula=None,
        capacidad=None,
        estado=None,
    ):
        self.id = id
        self.materia_id = materia_id
        self.profesor_id = profesor_id
        self.numero_seccion = numero_seccion
        self.periodo = periodo
        self.aula = aula
        self.capacidad = capacidad
        self.estado = estado

    @staticmethod
    def create(
        materia_id,
        profesor_id,
        numero_seccion,
        periodo,
        aula=None,
        capacidad=30,
        estado="activa",
    ):
        """Crea una nueva sección en la base de datos."""

        def _create():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                INSERT INTO secciones (id_materia, id_profesor, numero_seccion, periodo, aula, capacidad, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        materia_id,
                        profesor_id,
                        numero_seccion,
                        periodo,
                        aula,
                        capacidad,
                        estado,
                    ),
                )
                section_id = cursor.lastrowid
                if not section_id:
                    raise Exception(
                        "No se pudo obtener el ID de la sección recién creada"
                    )
                return section_id

        return execute_with_retry(_create)

    @staticmethod
    def get_by_id(section_id):
        """Obtiene una sección por su ID."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT id_seccion, id_materia, id_profesor, numero_seccion, periodo,  aula, capacidad, estado
                FROM secciones
                WHERE id_seccion = ?
                """,
                    (section_id,),
                )
                section_data = cursor.fetchone()
                if section_data:
                    return Section(
                        id=section_data[0],
                        materia_id=section_data[1],
                        profesor_id=section_data[2],
                        numero_seccion=section_data[3],
                        periodo=section_data[4],
                        aula=section_data[5],
                        capacidad=section_data[6],
                        estado=section_data[7],
                    )
                return None

        return execute_with_retry(_get)

    @staticmethod
    def get_by_professor(professor_id):
        """Obtiene todas las secciones de un profesor con información de materia, periodo, aula, sección, cantidad de estudiantes e id_seccion."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        m.nombre,           -- 0: nombre_materia
                        s.periodo,          -- 1: periodo
                        s.aula,             -- 2: aula
                        s.numero_seccion,   -- 3: sección
                        COUNT(i.id_inscripcion) as estudiantes, -- 4: estudiantes
                        s.id_seccion        -- 5: id_seccion
                    FROM secciones s
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN inscripciones i ON s.id_seccion = i.id_seccion
                    WHERE s.id_profesor = ?
                    GROUP BY s.id_seccion
                    ORDER BY s.periodo DESC, m.nombre
                    """,
                    (professor_id,),
                )
                sections = cursor.fetchall()
                return sections

        return execute_with_retry(_get)

    @staticmethod
    def get_all():
        """Obtiene todas las secciones con información de materia y profesor."""

        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                SELECT s.id_seccion, m.nombre, u.nombre || ' ' || u.apellido, 
                       s.numero_seccion, s.periodo, s.aula, s.capacidad, s.estado
                FROM secciones s
                JOIN materias m ON s.id_materia = m.id_materia
                JOIN profesores p ON s.id_profesor = p.id_profesor
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                """
                )
                sections = cursor.fetchall()
                return sections

        return execute_with_retry(_get)

    def update(
        self,
        materia_id=None,
        profesor_id=None,
        numero_seccion=None,
        periodo=None,
        aula=None,
        capacidad=None,
        estado=None,
    ):
        """Actualiza los datos de la sección."""

        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if materia_id is not None:
                    self.materia_id = materia_id
                if profesor_id is not None:
                    self.profesor_id = profesor_id
                if numero_seccion is not None:
                    self.numero_seccion = numero_seccion
                if periodo is not None:
                    self.periodo = periodo
                if aula is not None:
                    self.aula = aula
                if capacidad is not None:
                    self.capacidad = capacidad
                if estado is not None:
                    self.estado = estado
                cursor.execute(
                    """
                    UPDATE secciones
                    SET id_materia = ?, id_profesor = ?, numero_seccion = ?, periodo = ?, aula = ?, capacidad = ?, estado = ?
                    WHERE id_seccion = ?
                    """,
                    (
                        self.materia_id,
                        self.profesor_id,
                        self.numero_seccion,
                        self.periodo,
                        self.aula,
                        self.capacidad,
                        self.estado,
                        self.id,
                    ),
                )

        execute_with_retry(_update)
        return self

    @staticmethod
    def delete(section_id):
        """Elimina la sección de la base de datos."""

        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM secciones WHERE id_seccion = ?", (section_id,)
                )

        execute_with_retry(_delete)
