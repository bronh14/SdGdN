from models.grade import Grade
from models.enrollment import Enrollment
from datetime import datetime


class GradeController:
    def get_by_id(self, grade_id):
        """Obtiene una calificación por su ID."""
        return Grade.get_by_id(grade_id)

    def get_by_enrollment(self, enrollment_id):
        """Obtiene todas las calificaciones de una inscripción."""
        return Grade.get_by_enrollment(enrollment_id)

    def get_student_grades(self, student_id):
        """Obtiene todas las calificaciones de un estudiante."""
        return Grade.get_student_grades(student_id)

    def create(self, inscripcion_id, tipo_evaluacion, valor_nota, comentarios=None):
        """Crea una nueva calificación."""
        fecha_evaluacion = datetime.now().strftime("%Y-%m-%d")
        return Grade.create(
            inscripcion_id, tipo_evaluacion, valor_nota, fecha_evaluacion, comentarios
        )

    def update(self, grade_id, valor_nota=None, comentarios=None):
        """Actualiza los datos de una calificación."""
        grade = Grade.get_by_id(grade_id)
        if not grade:
            raise ValueError("Calificación no encontrada")

        return grade.update(valor_nota, comentarios)

    def get_students_by_section(self, section_id):
        """
        Retorna una lista de tuplas con los datos de los estudiantes inscritos en la sección.
        Puedes ajustar los campos según tu modelo de notas.
        """
        # Aquí puedes obtener los estudiantes inscritos en la sección
        enrollments = Enrollment.get_by_section(section_id)
        # Retorna: (C.I, Nombres, Apellidos, Corte1, Corte2, Corte3, Corte4, NotaDef)
        # Por ahora, solo retorna los datos básicos, puedes agregar los cortes si tienes esa info
        result = []
        for e in enrollments:
            # e = (id_inscripcion, cedula, nombre, apellido, fecha_inscripcion, estado)
            ci = e[1]
            nombres = e[2]
            apellidos = e[3]
            # Si tienes notas, agrégalas aquí. Por ahora, pon 0 o vacío.
            result.append((ci, nombres, apellidos, 0, 0, 0, 0, 0))
        return result

    def delete(self, grade_id):
        """Elimina una calificación."""
        grade = Grade.get_by_id(grade_id)
        if not grade:
            raise ValueError("Calificación no encontrada")

        grade.delete()
