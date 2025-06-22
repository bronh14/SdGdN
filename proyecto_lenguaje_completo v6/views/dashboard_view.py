import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from views.base_view import BaseView
from controllers.user_controller import UserController
from controllers.coordinator_controller import CoordinatorController
from controllers.professor_controller import ProfessorController
from controllers.student_controller import StudentController
from controllers.course_controller import CourseController
from controllers.section_controller import SectionController
from views.coordinator_views import CoordinatorListView
from views.professor_views import ProfessorListView
from views.student_views import StudentListView
from views.course_views import CourseListView
from views.section_views import SectionListView
from views.report_views import ReportView
from views.enrollment_view import EnrollmentView
from models.student import Student


class DashboardView(BaseView):
    def __init__(self, parent, app_controller, user):
        super().__init__(parent, app_controller)
        self.user = user
        self.user_controller = UserController()
        self.coordinator_controller = CoordinatorController()
        self.professor_controller = ProfessorController()
        self.student_controller = StudentController()
        self.course_controller = CourseController()
        self.section_controller = SectionController()

        # Crear interfaz principal
        self.create_main_interface()

    def create_main_interface(self):
        # Frame principal
        self.main_frame = tk.Frame(self.frame)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.main_frame, width=250, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Header del sidebar
        sidebar_header = tk.Frame(self.sidebar, bg="#2c3e50", height=150)
        sidebar_header.pack(fill="x")

        # Logo
        logo_label = tk.Label(
            sidebar_header, text="🎓", font=("Arial", 36), fg="white", bg="#2c3e50"
        )
        logo_label.pack(pady=(20, 5))

        # Información del usuario
        user_info = tk.Frame(sidebar_header, bg="#2c3e50")
        user_info.pack(fill="x", padx=10)

        user_name = tk.Label(
            user_info,
            text=f"{self.user.nombre} {self.user.apellido}",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        user_name.pack(anchor="w")

        user_role = tk.Label(
            user_info,
            text=f"Rol: {self.user.rol.capitalize()}",
            font=("Arial", 10),
            fg="white",
            bg="#2c3e50",
        )
        user_role.pack(anchor="w")

        user_id = tk.Label(
            user_info,
            text=f"Cédula: {self.user.cedula}",
            font=("Arial", 10),
            fg="white",
            bg="#2c3e50",
        )
        user_id.pack(anchor="w")

        # Separador
        separator = tk.Frame(self.sidebar, height=2, bg="#34495e")
        separator.pack(fill="x", padx=20, pady=10)

        # Menú según el rol
        self.create_menu_by_role()

        # Botón de cerrar sesión
        logout_btn = tk.Button(
            self.sidebar,
            text="Cerrar Sesión",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=10,
            pady=8,
            command=self.logout,
        )
        logout_btn.pack(side="bottom", fill="x", padx=20, pady=20)

        # Contenido principal
        self.content_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Mostrar dashboard inicial
        self.show_dashboard()

    def create_menu_by_role(self):
        # Crear menú SIDEBAR según el rol del usuario
        menu_items = {
            "administrador": [
                ("Dashboard", "📊", self.show_dashboard),
                ("Coordinadores", "🧑‍💼", self.show_coordinators),  # <-- NUEVO
                ("Profesores", "👨‍🏫", self.show_professors),
                ("Estudiantes", "👨‍🎓", self.show_students),
                ("Materias", "📚", self.show_courses),
                # ("Secciones", "🏛️", self.show_sections),
                ("Reportes", "📝", self.show_reports),
            ],
            "profesor": [
                ("Dashboard", "📊", self.show_dashboard),
                ("Mis Cursos", "📚", self.show_my_courses_professor),
                ("Gestión de Notas", "📝", self.show_grades_management),
                # ("Reportes", "📊", self.show_reports),
            ],
            "alumno": [
                ("Dashboard", "📊", self.show_dashboard),
                ("Inscripción", "✏️", self.show_enrollment),
                ("Mis Materias", "📚", self.show_my_courses_student),
                ("Reportes", "📜", self.show_reports),
            ],
            "coordinacion": [
                ("Dashboard", "📊", self.show_dashboard),
                ("Gestión de Profesores", "👨‍🏫", self.show_professor_courses),
                ("Gestión de Materias", "📚", self.show_courses),
                ("Gestión de Secciones", "🏛️", self.show_sections),
                ("Reportes", "📝", self.show_reports),
                # ("Estadísticas", "📊", self.show_statistics),
            ],
        }

        for text, icon, command in menu_items[self.user.rol]:
            menu_btn = tk.Button(
                self.sidebar,
                text=f" {icon} {text}",
                bg="#2c3e50",
                fg="white",
                font=("Arial", 11),
                bd=0,
                padx=10,
                pady=12,
                anchor="w",
                activebackground="#3498db",
                activeforeground="white",
                command=command,
            )
            menu_btn.pack(fill="x", padx=5, pady=1)

    def show_dashboard(self):
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame, text="Dashboard", font=("Arial", 16, "bold"), bg="white"
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Contenido del dashboard
        dashboard_frame = tk.Frame(self.content_frame, bg="#f5f5f5")
        dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tarjetas de información
        cards_frame = tk.Frame(dashboard_frame, bg="#f5f5f5")
        cards_frame.pack(fill="x")

        # Obtener estadísticas
        estudiantes_count = len(self.student_controller.get_all())
        coordinadores_count = len(self.coordinator_controller.get_all())
        profesores_count = len(self.professor_controller.get_all())
        materias_count = len(self.course_controller.get_all())
        secciones_count = len(self.section_controller.get_all())

        # Crear tarjetas
        card_data = [
            ("Estudiantes", estudiantes_count, "#3498db", "👨‍🎓"),
            ("Profesores", profesores_count, "#2ecc71", "👨‍🏫"),
            ("Materias", materias_count, "#f39c12", "📚"),
            ("Secciones", secciones_count, "#e74c3c", "🏛️"),
        ]

        for i, (title, count, color, icon) in enumerate(card_data):
            card = tk.Frame(
                cards_frame,
                bg="white",
                padx=15,
                pady=15,
                bd=0,
                highlightthickness=1,
                highlightbackground="#ddd",
            )
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            icon_label = tk.Label(
                card, text=icon, font=("Arial", 24), bg="white", fg=color
            )
            icon_label.pack(anchor="w")

            count_label = tk.Label(
                card, text=str(count), font=("Arial", 24, "bold"), bg="white"
            )
            count_label.pack(anchor="w")

            title_label = tk.Label(
                card, text=title, font=("Arial", 12), bg="white", fg="#555"
            )
            title_label.pack(anchor="w")

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        cards_frame.grid_columnconfigure(3, weight=1)

        # Gráficos
        charts_frame = tk.Frame(dashboard_frame, bg="#f5f5f5")
        charts_frame.pack(fill="both", expand=True, pady=20)

        # Gráfico de barras
        chart1_frame = tk.Frame(
            charts_frame,
            bg="white",
            padx=15,
            pady=15,
            bd=0,
            highlightthickness=1,
            highlightbackground="#ddd",
        )
        chart1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        chart_title = tk.Label(
            chart1_frame,
            text="Distribución por Rol",
            font=("Arial", 12, "bold"),
            bg="white",
        )
        chart_title.pack(anchor="w", pady=(0, 10))

        # Datos para el gráfico
        roles = ["Administrador", "Profesor", "Alumno", "Coordinación"]
        valores = [1, profesores_count, estudiantes_count, coordinadores_count]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(roles, valores, color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c"])
        ax.set_ylabel("Cantidad")
        ax.set_title("Usuarios por Rol")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

        canvas = FigureCanvasTkAgg(fig, master=chart1_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)

    def show_coordinators(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        coordinator_view = CoordinatorListView(
            self.content_frame, self.app_controller, self.user
        )

    def show_professors(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Mostrar vista de profesores
        professor_view = ProfessorListView(
            self.content_frame, self.app_controller, self.user
        )

    def show_students(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Mostrar vista de estudiantes
        student_view = StudentListView(
            self.content_frame, self.app_controller, self.user
        )

    def show_professor_courses(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Obtener la carrera del coordinador logueado
        coordinator = self.coordinator_controller.get_by_id(self.user.id)
        if not coordinator or not coordinator.carrera:
            from tkinter import messagebox

            messagebox.showerror(
                "Error", "No se pudo determinar la carrera del coordinador."
            )
            return

        carrera_coordinador = coordinator.carrera

        # Obtener todos los profesores y filtrar por carrera
        profesores = self.professor_controller.get_all()
        profesores_filtrados = [
            p for p in profesores if p[4] == carrera_coordinador
        ]  # p[4] es carrera

        # Crear encabezado
        header_frame = tk.Frame(self.content_frame, bg="white", height=60)
        header_frame.pack(fill="x")
        header_title = tk.Label(
            header_frame,
            text=f"Profesores de la carrera: {carrera_coordinador}",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Crear tabla de profesores
        table_frame = tk.Frame(self.content_frame, bg="#f5f5f5")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("Cédula", "Nombre", "Apellido", "Carrera", "Fecha Contratación")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)

        for prof in profesores_filtrados:
            # p[1]=cedula, p[2]=nombre, p[3]=apellido, p[4]=carrera, p[5]=fecha_contratacion
            tree.insert("", "end", values=(prof[1], prof[2], prof[3], prof[4], prof[5]))

        if not profesores_filtrados:
            no_data_label = tk.Label(
                table_frame,
                text="No hay profesores registrados para esta carrera.",
                font=("Arial", 12),
                bg="#f5f5f5",
                fg="#888",
            )
            no_data_label.pack(pady=20)

        # Botón de acción debajo de la tabla
        action_frame = tk.Frame(self.content_frame, bg="#f5f5f5")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))

        # asignar_btn = tk.Button(
        #     action_frame,
        #     text="Asignar Materia",
        #     bg="#f39c12",
        #     fg="white",
        #     font=("Arial", 10, "bold"),
        #     bd=0,
        #     padx=15,
        #     pady=5,
        #     # command=self.asignar_selected_professor,  # Implementar este método según necesidad
        # )
        # asignar_btn.pack(side="left", padx=5)

    def show_courses(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Mostrar vista de materias
        course_view = CourseListView(self.content_frame, self.app_controller, self.user)

    def show_sections(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Mostrar vista de secciones
        section_view = SectionListView(
            self.content_frame, self.app_controller, self.user
        )

    def show_my_courses_professor(self):
        # Mostrar las materias que imparte el profesor
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from views.professor_courses_view import ProfessorCoursesView

        ProfessorCoursesView(self.content_frame, self.user)

    def show_my_courses_student(self):
        # Mostrar las materias que ve el estudiante
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from views.student_courses_view import StudentCoursesView

        StudentCoursesView(self.content_frame, self.user)

    def show_grades_management(self):
        # Implementación para gestión de notas
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from views.professor_views import GestionNotasProfesorView

        GestionNotasProfesorView(self.content_frame, self.user)

    def show_enrollment(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Obtener el estudiante a partir del usuario logueado
        estudiante = Student.get_by_user_id(self.user.id)
        if estudiante is None:
            from tkinter import messagebox

            messagebox.showerror("Error", "No se encontró información del estudiante.")
            return
        from views.enrollment_view import EnrollmentView

        EnrollmentView(self.content_frame, estudiante)

    def show_academic_history(self):
        # Implementación para historial académico
        pass

    def show_reports(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Mostrar vista de reportes
        report_view = ReportView(self.content_frame, self.app_controller, self.user)

    def show_statistics(self):
        # Implementación para estadísticas
        pass

    # def logout(self):
    #     self.destroy()
    #     self.app_controller.logout()

    def logout(self):
        # 1. Limpiar completamente la ventana principal
        for widget in self.frame.winfo_children():
            widget.destroy()

        # 2. Crear un contenedor centrado para el mensaje de despedida
        feedback_container = tk.Frame(self.frame, bg="#f0f0f0")
        feedback_container.place(relx=0.5, rely=0.5, anchor="center")

        # 3. Mostrar icono y mensaje de despedida
        icon_label = tk.Label(
            feedback_container,
            text="👋",
            font=("Arial", 80),
            bg="#f0f0f0",
            fg="#3498db",
        )
        icon_label.pack(pady=(0, 10))

        self.message_label = tk.Label(
            feedback_container,
            text="Cerrando sesión",
            font=("Arial", 16),
            bg="#f0f0f0",
        )
        self.message_label.pack()

        # 4. Esperar 2 segundos y luego llamar al logout real
        # 5. Iniciar la animación y el proceso de logout
        self._animate_logout_message(0)
        self.frame.after(2000, self.app_controller.logout)

    def _animate_logout_message(self, dot_count):
        """Anima los puntos suspensivos en el mensaje de cierre de sesión."""
        # Si el widget todavía existe, actualiza el texto
        if self.message_label.winfo_exists():
            # Construir el texto con el número actual de puntos
            new_text = f"Cerrando sesión{'.' * (dot_count % 4)}"
            self.message_label.config(text=new_text)

            # Programar la próxima actualización
            self.frame.after(400, self._animate_logout_message, dot_count + 1)
