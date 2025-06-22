from config.database import get_connection


class Course:
    def __init__(
        self,
        id=None,
        codigo=None,
        nombre=None,
        creditos=None,
        requisitos=None,
        carrera=None,
        semestre=None,
    ):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.creditos = creditos
        self.requisitos = requisitos
        self.carrera = carrera
        self.semestre = semestre

    @staticmethod
    def create(codigo, nombre, creditos, requisitos=None, carrera=None, semestre=None):
        """Crea una nueva materia en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO materias (codigo, nombre, creditos, requisitos, carrera, semestre)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (codigo, nombre, creditos, requisitos, carrera, semestre),
        )

        course_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return Course(
            id=course_id,
            codigo=codigo,
            nombre=nombre,
            creditos=creditos,
            requisitos=requisitos,
            carrera=carrera,
            semestre=semestre,
        )

    @staticmethod
    def get_by_id(course_id):
        """Obtiene una materia por su ID."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT id_materia, codigo, nombre, creditos, requisitos, carrera, semestre
        FROM materias
        WHERE id_materia = ?
        """,
            (course_id,),
        )

        course_data = cursor.fetchone()
        conn.close()

        if course_data:
            return Course(
                id=course_data[0],
                codigo=course_data[1],
                nombre=course_data[2],
                creditos=int(course_data[3]) if course_data[3] else 0,
                requisitos=course_data[4],
                carrera=course_data[5],
                semestre=course_data[6],
            )
        return None

    @staticmethod
    def get_by_codigo(codigo):
        """Obtiene una materia por su código."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT id_materia, codigo, nombre, creditos, requisitos, carrera, semestre
        FROM materias
        WHERE codigo = ?
        """,
            (codigo,),
        )

        course_data = cursor.fetchone()
        conn.close()

        if course_data:
            return Course(
                id=course_data[0],
                codigo=course_data[1],
                nombre=course_data[2],
                creditos=int(course_data[3]) if course_data[3] else 0,
                requisitos=course_data[4],
                carrera=course_data[5],
                semestre=course_data[6],
            )
        return None

    @staticmethod
    def get_all():
        """Obtiene todas las materias."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT id_materia, codigo, nombre, creditos, requisitos, carrera, semestre
        FROM materias
        """
        )

        courses = []
        for course_data in cursor.fetchall():
            courses.append(
                Course(
                    id=course_data[0],
                    codigo=course_data[1],
                    nombre=course_data[2],
                    creditos=int(course_data[3]) if course_data[3] else 0,
                    requisitos=course_data[4],
                    carrera=course_data[5],
                    semestre=course_data[6],
                )
            )

        conn.close()
        return courses

    def update(self, nombre=None, creditos=None, requisitos=None, carrera=None):
        """Actualiza los datos de la materia."""
        conn = get_connection()
        cursor = conn.cursor()

        if nombre:
            self.nombre = nombre

        if creditos:
            self.creditos = creditos

        if requisitos:
            self.requisitos = requisitos

        if carrera:
            self.carrera = carrera

        cursor.execute(
            """
        UPDATE materias
        SET nombre = ?, creditos = ?, requisitos = ?, carrera = ?
        WHERE id_materia = ?
        """,
            (self.nombre, self.creditos, self.requisitos, self.carrera, self.id),
        )

        conn.commit()
        conn.close()

        return self

    def delete(self):
        """Elimina la materia de la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
        DELETE FROM materias
        WHERE id_materia = ?
        """,
            (self.id,),
        )

        conn.commit()
        conn.close()
