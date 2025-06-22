import sqlite3
import hashlib
from datetime import datetime
from contextlib import contextmanager
import time


def get_connection():
    """Establece y retorna una conexión a la base de datos con timeout."""
    conn = sqlite3.connect("academic_system.db", timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Mejora la concurrencia
    conn.execute("PRAGMA busy_timeout=30000")  # 30 segundos de timeout
    return conn


@contextmanager
def get_db_connection():
    """Context manager para manejo seguro de conexiones a la base de datos."""
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def get_carreras():
    """Devuelve una lista de carreras únicas desde la tabla materias."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT carrera FROM materias WHERE carrera IS NOT NULL AND carrera != ''"
        )
        carreras = [row[0] for row in cursor.fetchall()]
        return carreras


def get_estudiantes_por_carrera():
    """Devuelve una lista de tuplas (carrera, cantidad) de estudiantes por carrera."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT carrera, COUNT(*) as cantidad
            FROM estudiantes
            GROUP BY carrera
            ORDER BY cantidad DESC
            """
        )
        resultados = cursor.fetchall()
        return resultados


def get_all_estudiantes_info():
    """
    Devuelve una lista de tuplas (Nombre y Apellido, Cédula, Carrera, Semestre) de todos los estudiantes,
    ordenados por carrera y semestre.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.nombre || ' ' || u.apellido, u.cedula, e.carrera, e.semestre
            FROM usuarios u
            JOIN estudiantes e ON u.id_usuario = e.id_usuario
            ORDER BY e.carrera, e.semestre DESC
        """
        )
        rows = cursor.fetchall()
        return rows


def get_estudiantes_nombres_y_cantidad_por_materia():
    """
    Devuelve una lista de tuplas (nombre_materia, nombre_estudiante, cantidad_estudiantes_en_materia)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.nombre, u.nombre || ' ' || u.apellido,
                (SELECT COUNT(*) 
                FROM inscripciones i2
                JOIN secciones s2 ON i2.id_seccion = s2.id_seccion
                WHERE s2.id_materia = m.id_materia
                ) as cantidad
            FROM materias m
            JOIN secciones s ON m.id_materia = s.id_materia
            JOIN inscripciones i ON s.id_seccion = i.id_seccion
            JOIN estudiantes e ON i.id_estudiante = e.id_estudiante
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            """
        )
        resultados = cursor.fetchall()
        return resultados


def get_profesores_por_carrera():
    """
    Devuelve una lista de tuplas (carrera, cantidad_profesores)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT carrera, COUNT(*) as cantidad
            FROM profesores
            GROUP BY carrera
            """
        )
        resultados = cursor.fetchall()
        return resultados


def get_todos_los_profesores(carrera):
    """
    Devuelve una lista de tuplas con toda la información de los profesores de una carrera específica.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                u.nombre,
                u.apellido,
                u.cedula,
                p.carrera,
                p.fecha_contratacion
            FROM profesores p
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE p.carrera = ?
            ORDER BY u.apellido, u.nombre
            """,
            (carrera,),
        )
        resultados = cursor.fetchall()
        return resultados


def get_record_academico_by_student_id(estudiante_id):
    """
    Devuelve una lista de tuplas con:
    (codigo, materia, creditos, periodo, nota_def, estado)
    Prioriza materias archivadas (materias_cursadas). Si no hay, muestra inscripciones activas.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Primero, buscar en materias_cursadas
        cursor.execute(
            """
            SELECT 
                m.codigo,
                m.nombre,
                m.creditos,
                mc.periodo,
                mc.nota_final,
                mc.estado
            FROM materias_cursadas mc
            JOIN materias m ON mc.id_materia = m.id_materia
            WHERE mc.id_estudiante = ?
            ORDER BY mc.periodo, m.semestre, m.nombre
            """,
            (estudiante_id,),
        )
        records = cursor.fetchall()
        if records:
            return records
        # Si no hay materias archivadas, mostrar inscripciones activas
        cursor.execute(
            """
            SELECT 
                m.codigo,
                m.nombre,
                m.creditos,
                COALESCE(s.periodo, '') as periodo,
                (
                    SELECT c.valor_nota
                    FROM calificaciones c
                    WHERE c.id_inscripcion = i.id_inscripcion
                    AND c.tipo_evaluacion = 'nota_def'
                    LIMIT 1
                ) as nota_def,
                CASE
                    WHEN (
                        SELECT c.valor_nota
                        FROM calificaciones c
                        WHERE c.id_inscripcion = i.id_inscripcion
                        AND c.tipo_evaluacion = 'nota_def'
                        LIMIT 1
                    ) >= 10 THEN 'APROBÓ'
                    WHEN (
                        SELECT c.valor_nota
                        FROM calificaciones c
                        WHERE c.id_inscripcion = i.id_inscripcion
                        AND c.tipo_evaluacion = 'nota_def'
                        LIMIT 1
                    ) < 10 AND (
                        SELECT c.valor_nota
                        FROM calificaciones c
                        WHERE c.id_inscripcion = i.id_inscripcion
                        AND c.tipo_evaluacion = 'nota_def'
                        LIMIT 1
                    ) IS NOT NULL THEN 'REPROBÓ'
                    ELSE 'EN CURSO'
                END as estado
            FROM inscripciones i
            JOIN secciones s ON i.id_seccion = s.id_seccion
            JOIN materias m ON s.id_materia = m.id_materia
            WHERE i.id_estudiante = ?
            ORDER BY s.periodo, m.semestre, m.nombre
            """,
            (estudiante_id,),
        )
        return cursor.fetchall()


def get_estudiantes_por_semestre_por_carrera(carrera):
    """
    Devuelve los estudiantes agrupados por semestre, filtrados por carrera.
    Retorna un diccionario con semestres como claves y listas de estudiantes como valores.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                s.semestre,
                u.cedula,
                u.nombre,
                u.apellido,
                s.carrera,
                s.semestre
            FROM estudiantes s
            INNER JOIN usuarios u ON s.id_usuario = u.id_usuario
            WHERE s.carrera = ?
            ORDER BY s.semestre, u.apellido, u.nombre
            """,
            (carrera,),
        )

        estudiantes_por_semestre = {}
        for row in cursor.fetchall():
            semestre, cedula, nombre, apellido, carrera, semestre_num = row

            if semestre not in estudiantes_por_semestre:
                estudiantes_por_semestre[semestre] = []

            estudiantes_por_semestre[semestre].append(
                {
                    "cedula": cedula,
                    "nombre": nombre,
                    "apellido": apellido,
                    "carrera": carrera,
                    "semestre": semestre_num,
                }
            )

        return estudiantes_por_semestre


def get_profesores_por_materias_por_carrera(carrera):
    """
    Devuelve los profesores agrupados por materias, filtrados por carrera.
    Retorna un diccionario con materias como claves y listas de profesores como valores.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                u.cedula,
                u.nombre,
                u.apellido,
                p.carrera,
                p.fecha_contratacion,
                m.nombre as materia,
                s.numero_seccion
            FROM profesores p
            LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
            LEFT JOIN secciones s ON p.id_profesor = s.id_profesor
            LEFT JOIN materias m ON s.id_materia = m.id_materia
            WHERE p.carrera = ?
            ORDER BY u.apellido, u.nombre, m.nombre
            """,
            (carrera,),
        )

        profesores_por_materia = {}
        for row in cursor.fetchall():
            (
                cedula,
                nombre,
                apellido,
                carrera_prof,
                fecha_contratacion,
                materia,
                numero_seccion,
            ) = row

            materia_key = materia if materia else "SIN MATERIA"
            if materia_key not in profesores_por_materia:
                profesores_por_materia[materia_key] = []

            profesores_por_materia[materia_key].append(
                {
                    "cedula": cedula,
                    "nombre": nombre,
                    "apellido": apellido,
                    "carrera": carrera_prof,
                    "fecha_contratacion": fecha_contratacion,
                    "numero_seccion": numero_seccion,
                }
            )
        return profesores_por_materia


def get_total_estudiantes():
    """Devuelve el total de estudiantes registrados."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM estudiantes")
        total = cursor.fetchone()[0]
        return total


def execute_with_retry(func, max_retries=3, delay=0.1):
    """Ejecuta una función con reintentos en caso de database locked."""
    for attempt in range(max_retries):
        try:
            return func()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(delay * (2**attempt))  # Backoff exponencial
                continue
            raise e


def initialize_database():
    """Crea las tablas necesarias si no existen y añade datos iniciales."""

    def _initialize():
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Tabla de usuarios
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                contraseña_hash TEXT NOT NULL,
                rol TEXT NOT NULL CHECK (rol IN ('administrador', 'profesor', 'alumno', 'coordinacion'))
            )
            """
            )

            # Tabla de coordinadores
            cursor.execute(
                """ 
            CREATE TABLE IF NOT EXISTS coordinadores (
                id_coordinador INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                carrera TEXT,
                fecha_ingreso TEXT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
            """
            )

            # Tabla de profesores
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS profesores (
                id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                carrera TEXT,
                fecha_contratacion TEXT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
            """
            )

            # Tabla de estudiantes
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS estudiantes (
                id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                carrera TEXT,
                semestre INTEGER,
                fecha_ingreso TEXT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
            """
            )

            # Tabla de materias - CORREGIDA para permitir mismo código en diferentes carreras
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS materias (
                id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                creditos INTEGER NOT NULL,
                requisitos TEXT,
                carrera TEXT,
                semestre INTEGER NOT NULL,
                UNIQUE(codigo, carrera, semestre)
            )
            """
            )

            # Crear tabla de períodos académicos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS periodos_academicos (
                    id_periodo INTEGER PRIMARY KEY AUTOINCREMENT,
                    periodo TEXT NOT NULL UNIQUE,
                    es_activo BOOLEAN DEFAULT 0,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Insertar períodos actuales si no existen
            current_year = datetime.now().year
            periodos = [f"{current_year}-1", f"{current_year}-2"]

            for periodo in periodos:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO periodos_academicos (periodo, es_activo)
                    VALUES (?, 0)
                """,
                    (periodo,),
                )

            # Modificar tabla de secciones para incluir período
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS secciones (
                    id_seccion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_materia INTEGER NOT NULL,
                    numero_seccion INTEGER NOT NULL,
                    id_profesor INTEGER,
                    periodo TEXT NOT NULL,
                    aula TEXT,
                    capacidad INTEGER DEFAULT 30,
                    estado TEXT DEFAULT 'activa',
                    FOREIGN KEY (id_materia) REFERENCES materias(id_materia),
                    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
                    UNIQUE(id_materia, numero_seccion, periodo)
                )
            """
            )

            # Verificar si existe la columna periodo en la tabla secciones
            cursor.execute("PRAGMA table_info(secciones)")
            columns = [column[1] for column in cursor.fetchall()]

            if "periodo" not in columns:
                # Agregar columna periodo si no existe
                cursor.execute("ALTER TABLE secciones ADD COLUMN periodo TEXT")
                # Actualizar registros existentes con el período actual
                cursor.execute(
                    "UPDATE secciones SET periodo = ? WHERE periodo IS NULL",
                    (f"{current_year}-1",),
                )

            # Tabla de inscripciones
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS inscripciones (
                id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante INTEGER,
                id_seccion INTEGER,
                fecha_inscripcion TEXT,
                estado TEXT DEFAULT 'activo',
                FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
                FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion)
            )
            """
            )

            # Tabla de calificaciones
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS calificaciones (
                id_calificacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_inscripcion INTEGER,
                tipo_evaluacion TEXT NOT NULL,
                valor_nota REAL NOT NULL,
                fecha_evaluacion TEXT,
                comentarios TEXT,
                FOREIGN KEY (id_inscripcion) REFERENCES inscripciones(id_inscripcion)
            )
            """
            )

            # Tabla para registrar materias cursadas por estudiantes
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS materias_cursadas (
                id_cursada INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante INTEGER NOT NULL,
                id_materia INTEGER NOT NULL,
                periodo TEXT,
                nota_final REAL,
                estado TEXT NOT NULL CHECK (estado IN ('APROBÓ', 'REPROBÓ', 'REPITIÓ', 'REPARACIÓN')),
                fecha_cursada TEXT,
                FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
                FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
            )
            """
            )

            # Crear usuario administrador por defecto si no existe
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'administrador'")
            if cursor.fetchone()[0] == 0:
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute(
                    """
                INSERT INTO usuarios (cedula, nombre, apellido, contraseña_hash, rol)
                VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        "admin",
                        "Administrador",
                        "Sistema",
                        admin_password,
                        "administrador",
                    ),
                )

            # Verificar si la tabla materias ya existe y tiene datos
            cursor.execute("SELECT COUNT(*) FROM materias")
            if cursor.fetchone()[0] == 0:
                # Solo insertar materias si la tabla está vacía
                materias = [
                    (
                        "ADG-25132",
                        "EDUCACIÓN AMBIENTAL",
                        2,
                        None,
                        "Ingeniería en Sistemas",
                        1,
                    ),
                    (
                        "ADG-25132",
                        "EDUCACIÓN AMBIENTAL",
                        2,
                        None,
                        "Ingeniería Mecánica",
                        1,
                    ),
                    (
                        "ADG-25132",
                        "EDUCACIÓN AMBIENTAL",
                        2,
                        None,
                        "Ingeniería Naval",
                        1,
                    ),
                    (
                        "ADG-25123",
                        "HOMBRE, SOCIEDAD, CIENCIAS Y TECNOLOGÍA",
                        3,
                        None,
                        "Ingeniería en Sistemas",
                        1,
                    ),
                    (
                        "ADG-25123",
                        "HOMBRE, SOCIEDAD, CIENCIAS Y TECNOLOGÍA",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        1,
                    ),
                    (
                        "ADG-25123",
                        "HOMBRE, SOCIEDAD, CIENCIAS Y TECNOLOGÍA",
                        3,
                        None,
                        "Ingeniería Naval",
                        1,
                    ),
                    ("IDM-24113", "INGLÉS I", 3, None, "Ingeniería en Sistemas", 1),
                    ("IDM-24113", "INGLÉS I", 3, None, "Ingeniería Mecánica", 1),
                    ("IDM-24113", "INGLÉS I", 3, None, "Ingeniería Naval", 1),
                    ("MAT-21212", "DIBUJO", 2, None, "Ingeniería en Sistemas", 1),
                    ("MAT-21212", "DIBUJO", 2, None, "Ingeniería Mecánica", 1),
                    ("MAT-21212", "DIBUJO", 2, None, "Ingeniería Naval", 1),
                    ("MAT-21215", "MATEMÁTICA I", 5, None, "Ingeniería en Sistemas", 1),
                    ("MAT-21215", "MATEMÁTICA I", 5, None, "Ingeniería Mecánica", 1),
                    ("MAT-21215", "MATEMÁTICA I", 5, None, "Ingeniería Naval", 1),
                    (
                        "MAT-21524",
                        "GEOMETRÍA ANALÍTICA",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        1,
                    ),
                    (
                        "MAT-21524",
                        "GEOMETRÍA ANALÍTICA",
                        4,
                        None,
                        "Ingeniería Mecánica",
                        1,
                    ),
                    (
                        "MAT-21524",
                        "GEOMETRÍA ANALÍTICA",
                        4,
                        None,
                        "Ingeniería Naval",
                        1,
                    ),
                    ("ADG-25131", "SEMINARIO I", 1, None, "Ingeniería en Sistemas", 1),
                    ("ADG-25131", "SEMINARIO I", 1, None, "Ingeniería Mecánica", 1),
                    ("ADG-25131", "SEMINARIO I", 1, None, "Ingeniería Naval", 1),
                    (
                        "DIN-21113",
                        "DEFENSA INTEGRAL DE LA NACIÓN I",
                        3,
                        None,
                        "Ingeniería en Sistemas",
                        1,
                    ),
                    (
                        "DIN-21113",
                        "DEFENSA INTEGRAL DE LA NACIÓN I",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        1,
                    ),
                    (
                        "DIN-21113",
                        "DEFENSA INTEGRAL DE LA NACIÓN I",
                        3,
                        None,
                        "Ingeniería Naval",
                        1,
                    ),
                    (
                        "ACO-20110",
                        "ACTIVIDADES COMPLEMENTARIAS I (DEPORTE)",
                        0,
                        None,
                        "Ingeniería en Sistemas",
                        1,
                    ),
                    (
                        "ACO-20110",
                        "ACTIVIDADES COMPLEMENTARIAS I (DEPORTE)",
                        0,
                        None,
                        "Ingeniería Mecánica",
                        1,
                    ),
                    (
                        "ACO-20110",
                        "ACTIVIDADES COMPLEMENTARIAS I (DEPORTE)",
                        0,
                        None,
                        "Ingeniería Naval",
                        1,
                    ),
                    (
                        "IDM-24123",
                        "INGLÉS II",
                        3,
                        "IDM-24113",
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "IDM-24123",
                        "INGLÉS II",
                        3,
                        "IDM-24113",
                        "Ingeniería Mecánica",
                        2,
                    ),
                    ("IDM-24123", "INGLÉS II", 3, "IDM-24113", "Ingeniería Naval", 2),
                    (
                        "MAT-21225",
                        "MATEMÁTICA II",
                        5,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "MAT-21225",
                        "MATEMÁTICA II",
                        5,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería Mecánica",
                        2,
                    ),
                    (
                        "MAT-21225",
                        "MATEMÁTICA II",
                        5,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería Naval",
                        2,
                    ),
                    (
                        "MAT-21114",
                        "ÁLGEBRA LINEAL",
                        4,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "MAT-21114",
                        "ÁLGEBRA LINEAL",
                        4,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería Mecánica",
                        2,
                    ),
                    (
                        "MAT-21114",
                        "ÁLGEBRA LINEAL",
                        4,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería Naval",
                        2,
                    ),
                    (
                        "QUF-23015",
                        "FÍSICA I",
                        5,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "QUF-23015",
                        "FÍSICA I",
                        5,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería Mecánica",
                        2,
                    ),
                    (
                        "QUF-23015",
                        "FÍSICA I",
                        5,
                        "MAT-21215 / MAT-21524",
                        "Ingeniería Naval",
                        2,
                    ),
                    (
                        "QUF-22014",
                        "QUÍMICA GENERAL",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    ("QUF-22014", "QUÍMICA GENERAL", 4, None, "Ingeniería Mecánica", 2),
                    ("QUF-22014", "QUÍMICA GENERAL", 4, None, "Ingeniería Naval", 2),
                    (
                        "ADG-25133",
                        "SEMINARIO II",
                        1,
                        "ADG-25132",
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "ADG-25133",
                        "SEMINARIO II",
                        1,
                        "ADG-25132",
                        "Ingeniería Mecánica",
                        2,
                    ),
                    (
                        "ADG-25133",
                        "SEMINARIO II",
                        1,
                        "ADG-25132",
                        "Ingeniería Naval",
                        2,
                    ),
                    (
                        "DIN-21123",
                        "DEFENSA INTEGRAL DE LA NACIÓN II",
                        3,
                        "DIN-21113",
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "DIN-21123",
                        "DEFENSA INTEGRAL DE LA NACIÓN II",
                        3,
                        "DIN-21113",
                        "Ingeniería Mecánica",
                        2,
                    ),
                    (
                        "DIN-21123",
                        "DEFENSA INTEGRAL DE LA NACIÓN II",
                        3,
                        "DIN-21113",
                        "Ingeniería Naval",
                        2,
                    ),
                    (
                        "ACO-20111",
                        "ACTIVIDADES COMPLEMENTARIAS II (CULTURA)",
                        0,
                        None,
                        "Ingeniería en Sistemas",
                        2,
                    ),
                    (
                        "ACO-20111",
                        "ACTIVIDADES COMPLEMENTARIAS II (CULTURA)",
                        0,
                        None,
                        "Ingeniería Mecánica",
                        2,
                    ),
                    (
                        "ACO-20111",
                        "ACTIVIDADES COMPLEMENTARIAS II (CULTURA)",
                        0,
                        None,
                        "Ingeniería Naval",
                        2,
                    ),
                    (
                        "QUF-23025",
                        "FÍSICA II",
                        5,
                        "QUF-23015 / MAT-21225",
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "QUF-23025",
                        "FÍSICA II",
                        5,
                        "QUF-23015 / MAT-21225",
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "QUF-23025",
                        "FÍSICA II",
                        5,
                        "QUF-23015 / MAT-21225",
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "MAT-21235",
                        "MATEMÁTICA III",
                        5,
                        "MAT-21225",
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "MAT-21235",
                        "MATEMÁTICA III",
                        5,
                        "MAT-21225",
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "MAT-21235",
                        "MATEMÁTICA III",
                        5,
                        "MAT-21225",
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "MAT-21414",
                        "PROBABILIDAD Y ESTADÍSTICA",
                        4,
                        "MAT-21225",
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "MAT-21414",
                        "PROBABILIDAD Y ESTADÍSTICA",
                        4,
                        "MAT-21225",
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "MAT-21414",
                        "PROBABILIDAD Y ESTADÍSTICA",
                        4,
                        "MAT-21225",
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "SYC-22113",
                        "PROGRAMACIÓN",
                        3,
                        "MAT-21114",
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "SYC-22113",
                        "PROGRAMACIÓN",
                        3,
                        "MAT-21114",
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "SYC-22113",
                        "PROGRAMACIÓN",
                        3,
                        "MAT-21114",
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "NAV-20114",
                        "INTRODUCCIÓN A LOS SISTEMAS NAVALES",
                        4,
                        None,
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "DIN-21133",
                        "DEFENSA INTEGRAL DE LA NACIÓN III",
                        3,
                        "DIN-21123",
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "DIN-21133",
                        "DEFENSA INTEGRAL DE LA NACIÓN III",
                        3,
                        "DIN-21123",
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "DIN-21133",
                        "DEFENSA INTEGRAL DE LA NACIÓN III",
                        3,
                        "DIN-21123",
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "ACO-20130",
                        "ACTIVIDADES COMPLEMENTARIAS III (DEPORTE)",
                        0,
                        None,
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "ACO-20130",
                        "ACTIVIDADES COMPLEMENTARIAS III (DEPORTE)",
                        0,
                        None,
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "ACO-20130",
                        "ACTIVIDADES COMPLEMENTARIAS III (DEPORTE)",
                        0,
                        None,
                        "Ingeniería Naval",
                        3,
                    ),
                    (
                        "MAT-30265",
                        "MATEMÁTICAS APLICADA A LA INGENIERÍA",
                        5,
                        "MAT-21235",
                        "Ingeniería Naval",
                        4,
                    ),
                    (
                        "MEC-30115",
                        "MECÁNICA",
                        5,
                        "QUF-23025 / MAT-21235",
                        "Ingeniería Naval",
                        4,
                    ),
                    (
                        "QUF-30314",
                        "TERMODINÁMICA I",
                        4,
                        "QUF-23015 / MAT-21235",
                        "Ingeniería Naval",
                        4,
                    ),
                    (
                        "MAT-30123",
                        "GEOMETRÍA DESCRIPTIVA",
                        3,
                        "MAT-21212",
                        "Ingeniería Naval",
                        4,
                    ),
                    ("SYC-22114", "INFORMÁTICA", 4, "SYC-22113", "Ingeniería Naval", 4),
                    (
                        "MEC-30314",
                        "ELEMENTOS DE CIENCIAS DE LOS MATERIALES",
                        4,
                        "QUF-22014",
                        "Ingeniería Naval",
                        4,
                    ),
                    (
                        "DIN-31143",
                        "DEFENSA INTEGRAL DE LA NACIÓN IV",
                        3,
                        "DIN-21133",
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "DIN-31143",
                        "DEFENSA INTEGRAL DE LA NACIÓN IV",
                        3,
                        "DIN-21133",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "DIN-31143",
                        "DEFENSA INTEGRAL DE LA NACIÓN IV",
                        3,
                        "DIN-21133",
                        "Ingeniería Naval",
                        4,
                    ),
                    (
                        "ACO-20140",
                        "ACTIVIDADES COMPLEMENTARIAS IV (CULTURA)",
                        0,
                        None,
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "ACO-20140",
                        "ACTIVIDADES COMPLEMENTARIAS IV (CULTURA)",
                        0,
                        None,
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "ACO-20140",
                        "ACTIVIDADES COMPLEMENTARIAS IV (CULTURA)",
                        0,
                        None,
                        "Ingeniería Naval",
                        4,
                    ),
                    (
                        "NAV-30214",
                        "DIBUJO NAVAL",
                        4,
                        "MAT-30123",
                        "Ingeniería Naval",
                        5,
                    ),
                    ("MEC-30134", "MECANISMOS", 4, "MEC-30115", "Ingeniería Naval", 5),
                    (
                        "MEC-30215",
                        "RESISTENCIA DE LOS MATERIALES",
                        5,
                        "MEC-30115",
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "NAV-30714",
                        "EQUIPOS Y SERVICIOS",
                        4,
                        "NAV-20114 / CO NAV-302214",
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "NAV-30414",
                        "CONSTRUCCIÓN NAVAL I",
                        4,
                        "NAV-20114 / CO NAV-302215",
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "MEC-30414",
                        "MECÁNICA DE LOS FLUIDOS",
                        4,
                        "MEC-30115 / QUF-30314",
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "QUF-30323",
                        "TERMODINÁMICA II",
                        4,
                        "QUF-30314",
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "DIN-31153",
                        "DEFENSA INTEGRAL DE LA NACIÓN V",
                        3,
                        "DIN-31143",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "DIN-31153",
                        "DEFENSA INTEGRAL DE LA NACIÓN V",
                        3,
                        "DIN-31143",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "DIN-31153",
                        "DEFENSA INTEGRAL DE LA NACIÓN V",
                        3,
                        "DIN-31143",
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "ADG-10820",
                        "CÁTEDRA BOLIVARIANA I",
                        0,
                        None,
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "ADG-10820",
                        "CÁTEDRA BOLIVARIANA I",
                        0,
                        None,
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "ADG-10820",
                        "CÁTEDRA BOLIVARIANA I",
                        0,
                        None,
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "TAI-01",
                        "TALLER DE INDUCCIÓN AL SERVICIO COMUNITARIO",
                        0,
                        None,
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "TAI-01",
                        "TALLER DE INDUCCIÓN AL SERVICIO COMUNITARIO",
                        0,
                        None,
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "TAI-01",
                        "TALLER DE INDUCCIÓN AL SERVICIO COMUNITARIO",
                        0,
                        None,
                        "Ingeniería Naval",
                        5,
                    ),
                    (
                        "MEC-31413",
                        "TECNOLOGÍA MECÁNICA",
                        3,
                        "MEC-30314 / MEC-30215",
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "NAV-30424",
                        "CONSTRUCCIÓN NAVAL II",
                        4,
                        "NAV-30414 / NAV-30214",
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "NAV-30514",
                        "TEORÍA DEL BUQUE I",
                        4,
                        "NAV-20114 / NAV-30214",
                        "Ingeniería Naval",
                        6,
                    ),
                    ("MEC-31513", "SOLDADURA", 3, "MEC-30314", "Ingeniería Naval", 6),
                    (
                        "AGP-30213",
                        "HIGIENE Y SEGURIDAD INDUSTRIAL",
                        3,
                        None,
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "ADG-30214",
                        "METODOLOGÍA DE LA INVESTIGACIÓN",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    (
                        "ADG-30214",
                        "METODOLOGÍA DE LA INVESTIGACIÓN",
                        4,
                        None,
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "ADG-30214",
                        "METODOLOGÍA DE LA INVESTIGACIÓN",
                        4,
                        None,
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "ELC-30134",
                        "FUNDAMENTOS DE ELECTROTECNIA",
                        4,
                        "QUF-23025",
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "ENT-31223",
                        "ELECTIVA NO TÉCNICA (PLANIFIC. Y EVAL DE PROYECTOS)",
                        3,
                        None,
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    (
                        "ENT-31223",
                        "ELECTIVA NO TÉCNICA ",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "ENT-31223",
                        "ELECTIVA NO TÉCNICA (PLANIFIC. Y EVAL DE PROYECTOS)",
                        3,
                        None,
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "DIN-31163",
                        "DEFENSA INTEGRAL DE LA NACIÓN VI",
                        3,
                        "DIN-31153",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "DIN-31163",
                        "DEFENSA INTEGRAL DE LA NACIÓN VI",
                        3,
                        "DIN-31153",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "DIN-31163",
                        "DEFENSA INTEGRAL DE LA NACIÓN VI",
                        3,
                        "DIN-31153",
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "ADG-10821",
                        "CÁTEDRA BOLIVARIANA II",
                        0,
                        "ADG-10820",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "ADG-10821",
                        "CÁTEDRA BOLIVARIANA II",
                        0,
                        "ADG-10820",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "ADG-10821",
                        "CÁTEDRA BOLIVARIANA II",
                        0,
                        "ADG-10820",
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "PRO-01",
                        "PROYECTO DE SERVICIO COMUNITARIO",
                        0,
                        "TAI-01",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "PRO-01",
                        "PROYECTO DE SERVICIO COMUNITARIO",
                        0,
                        "TAI-01",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "PRO-01",
                        "PROYECTO DE SERVICIO COMUNITARIO",
                        0,
                        "TAI-01",
                        "Ingeniería Naval",
                        6,
                    ),
                    (
                        "NAV-30525",
                        "TEORÍA DEL BUQUE II",
                        4,
                        "NAV-30514 / MEC-30314",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "CIV-30114",
                        "CÁLCULOS DE ESTRUCTURAS",
                        4,
                        "MEC-30215",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "NAV-30814",
                        "ELECTRICIDAD APLICADA AL BUQUE",
                        4,
                        "ELC-30134",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "QUF-30414",
                        "TRANSFERENCIA DE CALOR",
                        4,
                        "QUF-30314",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "NAV-30314",
                        "PROPULSIÓN NAVAL",
                        4,
                        "MEC-30134 / QUF-30314",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "NAV-30614",
                        "MÁQUINAS MARINAS",
                        4,
                        "MEC-30514 / MEC-30414",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "EME-31113",
                        "ELECTIVA TÉCNICA (CORROSIÓN Y DESGASTE)",
                        3,
                        None,
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "DIN-31173",
                        "DEFENSA INTEGRAL DE LA NACIÓN VII",
                        3,
                        "DIN-31163",
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    (
                        "DIN-31173",
                        "DEFENSA INTEGRAL DE LA NACIÓN VII",
                        3,
                        "DIN-31163",
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "DIN-31173",
                        "DEFENSA INTEGRAL DE LA NACIÓN VII",
                        3,
                        "DIN-31163",
                        "Ingeniería Naval",
                        7,
                    ),
                    (
                        "NAV-30915",
                        "CÁLCULOS DE ESTRUCTURA DEL BUQUE",
                        5,
                        "NAV-30414 / CIV-30114",
                        "Ingeniería Naval",
                        8,
                    ),
                    (
                        "CJU-37314",
                        "MARCO LEGAL PARA EL EJERCICIO DE LA INGENIERÍA",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    (
                        "CJU-37314",
                        "MARCO LEGAL PARA EL EJERCICIO DE LA INGENIERÍA",
                        4,
                        None,
                        "Ingeniería Mecánica",
                        8,
                    ),
                    (
                        "CJU-37314",
                        "MARCO LEGAL PARA EL EJERCICIO DE LA INGENIERÍA",
                        4,
                        None,
                        "Ingeniería Naval",
                        8,
                    ),
                    (
                        "AGM-30314",
                        "MANTENIMIENTO GENERAL",
                        4,
                        None,
                        "Ingeniería Naval",
                        8,
                    ),
                    (
                        "NAV-30925",
                        "DISEÑO DEL BUQUE",
                        5,
                        "NAV-30424",
                        "Ingeniería Naval",
                        8,
                    ),
                    (
                        "EME-31143",
                        "ELECTIVA TÉCNICA (REFRIGERACIÓN Y AIRE ACOND.)",
                        3,
                        None,
                        "Ingeniería Naval",
                        8,
                    ),
                    (
                        "ENT -31143",
                        "ELECTIVA NO TÉCNICA (CALIDAD TOTAL)",
                        3,
                        None,
                        "Ingeniería Naval",
                        8,
                    ),
                    (
                        "DIN-31183",
                        "DEFENSA INTEGRAL DE LA NACIÓN VIII",
                        3,
                        "DIN-31173",
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    (
                        "DIN-31183",
                        "DEFENSA INTEGRAL DE LA NACIÓN VIII",
                        3,
                        "DIN-31173",
                        "Ingeniería Mecánica",
                        8,
                    ),
                    (
                        "DIN-31183",
                        "DEFENSA INTEGRAL DE LA NACIÓN VIII",
                        3,
                        "DIN-31173",
                        "Ingeniería Naval",
                        8,
                    ),
                    ("PST-30010", "PASANTÍAS", 10, None, "Ingeniería Naval", 9),
                    (
                        "MAT-20814",
                        "CÁLCULO NUMÉRICO",
                        4,
                        "MAT-21225/CO-MAT-21235",
                        "Ingeniería Mecánica",
                        3,
                    ),
                    (
                        "MAT-30265",
                        "MATEMÁTICAS APLICADA A LA INGENIERÍA",
                        5,
                        "MAT-21235",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "MEC-30115",
                        "MECÁNICA",
                        5,
                        "QUF-23025 / MAT-21235",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "QUF-30314",
                        "TERMODINÁMICA I",
                        4,
                        "QUF-23015 / MAT-21235",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "MAT-30123",
                        "GEOMETRÍA DESCRIPTIVA",
                        3,
                        "MAT-21212",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "SYC-30114",
                        "INFORMÁTICA",
                        4,
                        "SYC-22113",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "MEC-30314",
                        "ELEMENTOS DE CIENCIAS DE LOS MATERIALES",
                        4,
                        "QUF-22014",
                        "Ingeniería Mecánica",
                        4,
                    ),
                    (
                        "QUF-30323",
                        "TERMODINÁMICA II",
                        5,
                        "QUF-30314",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "MEC-30215",
                        "RESISTENCIA DE LOS MATERIALES",
                        5,
                        "MEC-30115",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "MEC-30414",
                        "MECÁNICA DE LOS FLUIDOS",
                        4,
                        "MEC-30115 / QUF-30314",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "ELC-30315",
                        "ELECTROTECNIA",
                        5,
                        "QUF-23025",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "MEC-30124",
                        "DIBUJO MECÁNICO",
                        4,
                        "MAT-30123",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "MEC-30614",
                        "PROCESOS DE FABRICACIÓN I",
                        4,
                        "CO-MEC-30215/MEC-30314",
                        "Ingeniería Mecánica",
                        5,
                    ),
                    (
                        "MEC-30134",
                        "MECANISMOS",
                        4,
                        "MEC-30115",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "MEC-30514",
                        "TRANSFERENCIA DE CALOR",
                        4,
                        "QUF-30115",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    ("SYC-30814", "SISTEMAS", 4, "MAT-30265", "Ingeniería Mecánica", 6),
                    (
                        "MEC-30714",
                        "DINÁMICA DE GASES",
                        4,
                        "QUF-314/MEC-30414",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "MEC-30625",
                        "PROCESOS DE FABRICACIÓN II",
                        5,
                        "MEC-30614",
                        "Ingeniería Mecánica",
                        6,
                    ),
                    (
                        "MEC-30925",
                        "VIBRACIONES MECÁNICAS",
                        5,
                        "MEC-30134",
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "MEC-30815",
                        "DISEÑO DE ELEMENTOS DE MÁQUINAS I",
                        5,
                        "MEC-30115/CO-MEC-30915",
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "AGP-30213",
                        "HIGIENE Y SEGURIDAD INDUSTRIAL",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "AGM-30314",
                        "MANTENIMIENTO GENERAL",
                        5,
                        None,
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "ENT-00001",
                        "ELECTIVA TÉCNICA ",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        7,
                    ),
                    (
                        "MEC-30825",
                        "DISEÑO DE ELEMENTOS DE MÁQUINAS II",
                        5,
                        "MEC-30815",
                        "Ingeniería Mecánica",
                        8,
                    ),
                    (
                        "MEC-31015",
                        "TURBOMÁQUINAS",
                        5,
                        "MEC-30414",
                        "Ingeniería Mecánica",
                        8,
                    ),
                    (
                        "MEC-31115",
                        "GENERACIÓN DE POTENCIA",
                        5,
                        "MEC-30825",
                        "Ingeniería Mecánica",
                        8,
                    ),
                    (
                        "ENT-00002",
                        "ELECTIVA NO TÉCNICA ",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        8,
                    ),
                    (
                        "ENT-00003",
                        "ELECTIVA TÉCNICA ",
                        3,
                        None,
                        "Ingeniería Mecánica",
                        8,
                    ),
                    ("PST-30010", "PASANTÍAS", 10, None, "Ingeniería Mecánica", 9),
                    (
                        "AGG-22313",
                        "SISTEMAS ADMINISTRATIVOS",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        3,
                    ),
                    (
                        "SYC-32114",
                        "TEORÍA DE LOS SISTEMAS",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "MAT-31714",
                        "CÁLCULO NUMÉRICO",
                        4,
                        "MAT-21235",
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "MAT-31214",
                        "LÓGICA MATEMÁTICA",
                        4,
                        "MAT-21114",
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "SYC-32225",
                        "LENGUAJE DE PROGRAMACIÓN I",
                        5,
                        "SYC-22113",
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "SYC-32414",
                        "PROCESAMIENTO DE DATOS",
                        4,
                        "SYC-22113",
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "AGL-30214",
                        "SISTEMAS DE PRODUCCIÓN",
                        4,
                        "AGG-22313",
                        "Ingeniería en Sistemas",
                        4,
                    ),
                    (
                        "SYC-32235",
                        "LENGUAJE DE PROGRAMACIÓN II",
                        5,
                        "SYC-32225",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "MAT-31114",
                        "TEORÍA DE GRAFOS",
                        4,
                        "MAT-31214/MAT-21414",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "MAT-30925",
                        "INVESTIGACIÓN DE OPERACIONES",
                        5,
                        "MAT-31714",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "ELN-30514",
                        "CIRCUITOS LÓGICOS",
                        4,
                        "MAT-31214",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "SYC-32514",
                        "ANÁLISIS DE SISTEMAS",
                        4,
                        "SYC-32114",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "SYC-32614",
                        "BASE DE DATOS",
                        4,
                        "SYC-32114",
                        "Ingeniería en Sistemas",
                        5,
                    ),
                    (
                        "MAT-30935",
                        "OPTIMIZACIÓN NO LINEAL",
                        5,
                        "MAT-30925",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "SYC-32245",
                        "LENGUAJE DE PROGRAMACIÓN III",
                        5,
                        "SYC-32235",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "MAT-31414",
                        "PROCESOS ESTOCÁSTICOS",
                        4,
                        "MAT-30925/MAT-31114",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "SYC-30525",
                        "ARQUITECTURA DEL COMPUTADOR",
                        5,
                        "ELN-30514",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "SYC-32524",
                        "DISEÑO DE SISTEMAS",
                        4,
                        "SYC-32514",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "SYC-30834",
                        "SISTEMAS OPERATIVOS",
                        4,
                        "CO-SYC-30525",
                        "Ingeniería en Sistemas",
                        6,
                    ),
                    (
                        "SYC-32714",
                        "IMPLANTACIÓN DE SISTEMAS",
                        4,
                        "SYC-32524",
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    (
                        "MAT-30945",
                        "SIMULACIÓN Y MODELOS",
                        5,
                        "MAT-30935/MAT-31414",
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    ("SYC-31644", "REDES", 4, "SYC-30834", "Ingeniería en Sistemas", 7),
                    (
                        "ADG-39224",
                        "GERENCIA DE LA INFORMÁTICA",
                        4,
                        None,
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    (
                        "ENT-00004",
                        "ELECTIVA TÉCNICA ",
                        3,
                        None,
                        "Ingeniería en Sistemas",
                        7,
                    ),
                    (
                        "MAT-31314",
                        "TEORÍA DE DECISIONES",
                        4,
                        "MAT-30945",
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    (
                        "SYC-32814",
                        "AUDITORIA DE SISTEMAS",
                        4,
                        "SYC-32714",
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    (
                        "TTC-31154",
                        "TELEPROCESOS",
                        4,
                        "SYC-31644",
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    (
                        "ENT-00005",
                        "ELECTIVA TÉCNICA ",
                        3,
                        None,
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    (
                        "ENT-00006",
                        "ELECTIVA NO TÉCNICA ",
                        3,
                        None,
                        "Ingeniería en Sistemas",
                        8,
                    ),
                    ("PST-30010", "PASANTÍAS", 10, None, "Ingeniería en Sistemas", 9),
                    ("CSL-10112", "PSICOLOGÍA GENERAL", 2, None, "Enfermería", 1),
                    (
                        "ADG-10812",
                        "SALUD Y DESARROLLO ECONÓMICO SOCIAL",
                        2,
                        None,
                        "Enfermería",
                        1,
                    ),
                    ("CSL-10317", "ENFERMERÍA BÁSICA", 7, None, "Enfermería", 1),
                    ("CSL-10622", "NUTRICIÓN Y DIETÉTICA", 2, None, "Enfermería", 1),
                    ("CSL-10214", "MORFOLOGÍA", 4, None, "Enfermería", 1),
                    (
                        "DIN-11113",
                        "DEFENSA INTEGRAL DE LA NACIÓN I",
                        3,
                        None,
                        "Enfermería",
                        1,
                    ),
                    (
                        "ACO-20110",
                        "ACTIVIDADES COMPLEMENTARIAS I (DEPORTE)",
                        0,
                        None,
                        "Enfermería",
                        1,
                    ),
                    ("CSL-10613", "BIOQUÍMICA", 3, "CSL-10214", "Enfermería", 2),
                    (
                        "CSL-10717",
                        "ENFERMERÍA MATERNO INFANTIL I",
                        7,
                        "CSL-10317/CSL-10214/CSL-10112",
                        "Enfermería",
                        2,
                    ),
                    ("IDM-10122", "INGLÉS INSTRUMENTAL", 2, None, "Enfermería", 2),
                    (
                        "CSL-10512",
                        "ESTADÍSTICA BIOESTADÍSTICA Y EPIDEMIOLOGÍA",
                        2,
                        None,
                        "Enfermería",
                        2,
                    ),
                    ("CSL-10224", "ANATOMÍA HUMANA", 4, "CSL-10214", "Enfermería", 2),
                    ("ADG-10822", "SOCIOANTROPOLOGÍA", 2, "ADG-10812", "Enfermería", 2),
                    (
                        "DIN-11123",
                        "DEFENSA INTEGRAL DE LA NACIÓN II",
                        3,
                        "DIN-11113",
                        "Enfermería",
                        2,
                    ),
                    (
                        "ACO-20111",
                        "ACTIVIDADES COMPLEMENTARIAS I (CULTURA)",
                        0,
                        None,
                        "Enfermería",
                        2,
                    ),
                    ("CSL-10623", "FARMACOLOGÍA", 3, "CSL-10613", "Enfermería", 3),
                    (
                        "CSL-10812",
                        "MICROBIOLOGÍA Y PARASITOLOGÍA",
                        2,
                        "CSL-10224/CSL-10512",
                        "Enfermería",
                        3,
                    ),
                    (
                        "CSL-10727",
                        "ENFERMERÍA MATERNO INFANTIL II",
                        7,
                        "CSL-10717",
                        "Enfermería",
                        3,
                    ),
                    (
                        "CSL-11017",
                        "ENFERMERÍA MÉDICO QUIRÚRGICO I",
                        7,
                        "CSL-10317/CSL-10224",
                        "Enfermería",
                        3,
                    ),
                    ("CSL-10922", "ÉTICA DE LA ENFERMERÍA", 2, None, "Enfermería", 3),
                    (
                        "CSL-10915",
                        "FISIOLOGÍA Y FISIOPATOLOGÍA",
                        5,
                        "CSL-10224/CO-CSL-10727/CO-CSL-11017",
                        "Enfermería",
                        3,
                    ),
                    ("ADG-10820", "CÁTEDRA BOLIVARIANA I", 0, None, "Enfermería", 3),
                    (
                        "DIN-11133",
                        "DEFENSA INTEGRAL DE LA NACIÓN III",
                        3,
                        "DIN-11123",
                        "Enfermería",
                        3,
                    ),
                    (
                        "ACO-20130",
                        "ACTIVIDADES COMPLEMENTARIAS I (DEPORTE)",
                        0,
                        None,
                        "Enfermería",
                        3,
                    ),
                    (
                        "CSL-11116",
                        "ENFERMERÍA EN SALUD MENTAL Y PSIQUIATRÍA",
                        6,
                        "CSL-10112",
                        "Enfermería",
                        4,
                    ),
                    (
                        "ADG-10213",
                        "METODOLOGÍA DE LA INVESTIGACIÓN",
                        4,
                        None,
                        "Enfermería",
                        4,
                    ),
                    (
                        "CSL-11027",
                        "ENFERMERÍA MÉDICO QUIRÚRGICO II",
                        7,
                        "CSL-11017",
                        "Enfermería",
                        4,
                    ),
                    (
                        "AGG-11414",
                        "ADMINISTRACIÓN DE LA ATENCIÓN DE ENFERMERÍA",
                        4,
                        "CSL-11017/CO-CSL-11116",
                        "Enfermería",
                        4,
                    ),
                    (
                        "CSL-11217",
                        "ENFERMERÍA COMUNITARIA E INVESTIGACIÓN APLICADA",
                        7,
                        "CO-ADG-10213",
                        "Enfermería",
                        4,
                    ),
                    (
                        "ADG-10821",
                        "CÁTEDRA BOLIVARIANA II",
                        0,
                        "ADG-10820",
                        "Enfermería",
                        4,
                    ),
                    (
                        "DIN-11143",
                        "DEFENSA INTEGRAL DE LA NACIÓN IV",
                        3,
                        "DIN-11133",
                        "Enfermería",
                        4,
                    ),
                    ("IRA-30303", "PASANTÍA HOSPITALARIA", 3, None, "Enfermería", 5),
                    ("IRC-30303", "PASANTÍA COMUNITARIA", 3, None, "Enfermería", 5),
                ]

                # Usar INSERT OR IGNORE para evitar errores de duplicados
                for materia in materias:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO materias (codigo, nombre, creditos, requisitos, carrera, semestre)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        materia,
                    )

            # Verificar si necesitamos agregar la columna numero_seccion a secciones existentes
            try:
                cursor.execute("SELECT numero_seccion FROM secciones LIMIT 1")
            except sqlite3.OperationalError:
                # La columna no existe, agregarla
                cursor.execute(
                    "ALTER TABLE secciones ADD COLUMN numero_seccion INTEGER DEFAULT 1"
                )

                # Actualizar secciones existentes para que tengan numero_seccion apropiado
                cursor.execute(
                    """
                    UPDATE secciones 
                    SET numero_seccion = (
                        SELECT COUNT(*) 
                        FROM secciones s2 
                        WHERE s2.id_materia = secciones.id_materia 
                        AND s2.id_seccion <= secciones.id_seccion
                    )
                """
                )

            # Confirmar los cambios
            conn.commit()

    # Ejecutar con reintentos
    execute_with_retry(_initialize)


def get_periodo_activo():
    """Obtiene el período académico activo actual"""

    def _get_periodo():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT periodo FROM periodos_academicos 
                WHERE es_activo = 1 
                LIMIT 1
            """
            )
            result = cursor.fetchone()
            return result[0] if result else None

    return execute_with_retry(_get_periodo)


def set_periodo_activo(periodo):
    """Establece un período académico como activo"""

    def _set_periodo():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Primero desactivar todos los períodos
            cursor.execute("UPDATE periodos_academicos SET es_activo = 0")
            # Luego activar el período seleccionado
            cursor.execute(
                """
                UPDATE periodos_academicos 
                SET es_activo = 1 
                WHERE periodo = ?
            """,
                (periodo,),
            )
            conn.commit()

    execute_with_retry(_set_periodo)


def get_periodos_disponibles():
    """Obtiene la lista de períodos académicos disponibles"""

    def _get_periodos():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT periodo, es_activo 
                FROM periodos_academicos 
                ORDER BY periodo DESC
            """
            )
            return cursor.fetchall()

    return execute_with_retry(_get_periodos)


if __name__ == "__main__":
    # Inicializar la base de datos
    initialize_database()
    print("Base de datos inicializada correctamente")
