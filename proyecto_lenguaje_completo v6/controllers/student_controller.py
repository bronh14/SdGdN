from models.student import Student
from models.user import User


class StudentController:
    def get_all(self):
        """Obtiene todos los estudiantes."""
        return Student.get_all()

    def get_by_id(self, student_id):
        """Obtiene un estudiante por su ID."""
        return Student.get_by_id(student_id)

    def get_id_by_cedula(self, cedula):
        """Obtiene el id_usuario de un profesor por su cédula."""
        students = self.get_all()
        for p in students:
            if str(p[1]) == str(cedula):  # p[1] es cedula
                return p[0]  # p[0] es id_usuario
        return None

    def update(
        self,
        student_id,
        cedula=None,
        nombre=None,
        apellido=None,
        carrera=None,
        semestre=None,
    ):
        """Actualiza los datos de un estudiante y su usuario."""
        student = Student.get_by_id(student_id)
        if not student:
            raise ValueError("Estudiante no encontrado")
        # Actualizar usuario
        user = User.get_by_id(student.user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        user.update(cedula=cedula, nombre=nombre, apellido=apellido)
        # Actualizar estudiante
        return student.update(carrera, semestre)

    def delete(self, student_id):
        """Elimina un estudiante."""
        student = Student.get_by_id(student_id)
        if not student:
            raise ValueError("Estudiante no encontrado")
        return Student.delete(student_id)
