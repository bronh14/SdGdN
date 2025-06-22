from models.course import Course


class CourseController:
    def get_all(self):
        """Obtiene todas las materias."""
        return Course.get_all()

    def get_by_id(self, course_id):
        """Obtiene una materia por su ID."""
        return Course.get_by_id(course_id)

    def get_by_codigo(self, codigo):
        """Obtiene una materia por su código."""
        return Course.get_by_codigo(codigo)

    def create(
        self, codigo, nombre, creditos, requisitos=None, carrera=None, semestre=None
    ):
        """Crea una nueva materia."""
        return Course.create(codigo, nombre, creditos, requisitos, carrera, semestre)

    def update(
        self,
        course_id,
        nombre=None,
        creditos=None,
        requisitos=None,
        carrera=None,
        semestre=None,
    ):
        """Actualiza los datos de una materia."""
        course = Course.get_by_id(course_id)
        if not course:
            raise ValueError("Materia no encontrada")

        return course.update(nombre, creditos, requisitos, carrera, semestre)

    def delete(self, course_id):
        """Elimina una materia."""
        course = Course.get_by_id(course_id)
        if not course:
            raise ValueError("Materia no encontrada")

        course.delete()
