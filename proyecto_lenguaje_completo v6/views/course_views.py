import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from controllers.course_controller import CourseController


class CourseListView:
    def __init__(self, parent, app_controller, user):
        self.parent = parent
        self.app_controller = app_controller
        self.user = user
        self.course_controller = CourseController()
        self.current_courses = []

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("Filtro.TLabel", background="#f5f5f5")
        style.configure(
            "Filtro.TCombobox", fieldbackground="#f5f5f5", background="#f5f5f5"
        )
        style.configure("Filter.TFrame", background="#f5f5f5")
        style.configure("Filter.TButton", background="#3498db", foreground="white")

        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Gestión de Materias",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Botón para agregar nuevo
        # add_btn = tk.Button(
        #     header_frame,
        #     text="Agregar Materia",
        #     bg="#2ecc71",
        #     fg="white",
        #     font=("Arial", 10, "bold"),
        #     bd=0,
        #     padx=15,
        #     pady=5,
        #     command=self.show_add_form,
        # )
        # add_btn.pack(side="right", padx=20, pady=15)

        # Contenido
        content_container = tk.Frame(self.parent, bg="#f5f5f5")
        content_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Barra de búsqueda
        search_frame = tk.Frame(content_container, bg="white", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(0, 20))

        search_label = tk.Label(search_frame, text="Buscar:", bg="white")
        search_label.pack(side="left", padx=(0, 10))

        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left")

        search_btn = tk.Button(
            search_frame,
            text="Buscar",
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            bd=0,
            padx=10,
            pady=2,
            command=self.search_courses,
        )
        search_btn.pack(side="left", padx=10)

        # Tabla
        table_frame = tk.Frame(content_container, bg="white")
        table_frame.pack(fill="both", expand=True)

        # Configurar columnas
        columns = (
            "id",
            "codigo",
            "nombre",
            "semestre",
            "carrera",
            "creditos",
            "requisitos",
        )

        # Filtros
        filter_frame = ttk.Frame(self.parent, style="Filter.TFrame")
        filter_frame.pack(pady=10)

        ttk.Label(filter_frame, text="Carrera:", style="Filtro.TLabel").pack(
            side="left"
        )
        self.carrera_var = tk.StringVar()
        self.carrera_combo = ttk.Combobox(
            filter_frame, textvariable=self.carrera_var, width=25, state="readonly"
        )
        self.carrera_combo.pack(side="left", padx=5)
        self.carrera_combo.bind("<<ComboboxSelected>>", self.on_carrera_selected)

        ttk.Label(filter_frame, text="Semestre:", style="Filtro.TLabel").pack(
            side="left"
        )
        self.semestre_var = tk.StringVar()
        self.semestre_combo = ttk.Combobox(
            filter_frame, textvariable=self.semestre_var, width=10, state="readonly"
        )
        self.semestre_combo.pack(side="left", padx=5)

        filter_btn = ttk.Button(
            filter_frame,
            text="Filtrar",
            command=self.apply_filters,
            style="Filter.TButton",
        )
        filter_btn.pack(side="left", padx=10)

        # Crear Treeview
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Configurar scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Configurar encabezados
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="center")

        # Cargar datos
        self.load_courses()

        # Menú contextual
        # self.tree.bind("<Double-1>", self.on_item_double_click)

        # Botones de acción
        action_frame = tk.Frame(content_container, bg="#f5f5f5", pady=10)
        action_frame.pack(fill="x")

        # edit_btn = tk.Button(
        #     action_frame,
        #     text="Editar",
        #     bg="#f39c12",
        #     fg="white",
        #     font=("Arial", 10, "bold"),
        #     bd=0,
        #     padx=15,
        #     pady=5,
        #     command=self.edit_selected_course,
        # )
        # edit_btn.pack(side="left", padx=5)

        # delete_btn = tk.Button(
        #     action_frame,
        #     text="Eliminar",
        #     bg="#e74c3c",
        #     fg="white",
        #     font=("Arial", 10, "bold"),
        #     bd=0,
        #     padx=15,
        #     pady=5,
        #     command=self.delete_selected_course,
        # )
        # delete_btn.pack(side="left", padx=5)

        refresh_btn = tk.Button(
            action_frame,
            text="Actualizar",
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.load_courses,
        )
        refresh_btn.pack(side="left", padx=5)

    def get_coordinator_carrera(self, user_id):
        from config.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT carrera FROM coordinadores WHERE id_usuario = ?", (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_professor_carrera(self, user_id):
        from config.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT carrera FROM profesores WHERE id_usuario = ?", (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_student_carrera(self, user_id):
        from config.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT carrera FROM estudiantes WHERE id_usuario = ?", (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_user_carrera(self):
        if getattr(self.user, "id", None) == 1:
            return None  # Admin, no filtrar
        rol = getattr(self.user, "rol", None)
        user_id = getattr(self.user, "id", None)
        if rol == "profesor":
            return self.get_professor_carrera(user_id)
        elif rol == "coordinacion":
            return self.get_coordinator_carrera(user_id)
        elif rol == "estudiante":
            return self.get_student_carrera(user_id)
        return None

    def load_courses(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        user_id = getattr(self.user, "id", None)
        user_rol = getattr(self.user, "rol", None)

        # Obtener materias
        courses = self.course_controller.get_all()

        if user_id == 1:
            pass  # Admin ve todas las materias
        elif user_rol == "coordinacion":
            carrera = self.get_coordinator_carrera(user_id)
            courses = [c for c in courses if c.carrera == carrera]
        else:
            courses = []

        self.current_courses = courses

        # Opciones de filtro según usuario
        if user_id == 1:
            semestres = sorted(
                {
                    str(course.semestre)
                    for course in self.course_controller.get_all()
                    if course.semestre is not None
                }
            )
            carreras = sorted(
                {
                    str(course.carrera)
                    for course in self.course_controller.get_all()
                    if course.carrera is not None
                }
            )
            self.carrera_combo["values"] = [""] + carreras
        elif user_rol == "coordinacion":
            semestres = sorted(
                {
                    str(course.semestre)
                    for course in courses
                    if course.semestre is not None
                }
            )
            self.carrera_combo["values"] = [self.carrera_var.get()]
        else:
            semestres = []
            self.carrera_combo["values"] = [self.carrera_var.get()]
        self.semestre_combo["values"] = [""] + semestres

        # Insertar datos en la tabla con id incremental
        for idx, course in enumerate(courses, 1):
            self.tree.insert(
                "",
                "end",
                values=(
                    idx,  # ID incremental
                    course.codigo,
                    course.nombre,
                    course.semestre,
                    course.carrera,
                    course.creditos,
                    course.requisitos,
                ),
            )

    def apply_filters(self):
        semestre = self.semestre_var.get()
        carrera = self.carrera_var.get()
        user_id = getattr(self.user, "id", None)
        user_rol = getattr(self.user, "rol", None)
        cursos = self.course_controller.get_all()
        filtrados = []

        if user_id == 1:
            for course in cursos:
                if carrera and str(course.carrera) != carrera:
                    continue
                if semestre and str(course.semestre) != semestre:
                    continue
                filtrados.append(course)
        elif user_rol == "coordinacion":
            for course in cursos:
                if str(course.carrera) != carrera:
                    continue
                if semestre and str(course.semestre) != semestre:
                    continue
                filtrados.append(course)
        elif user_rol == "profesor":
            for course in cursos:
                if str(course.carrera) != carrera:
                    continue
                if semestre and str(course.semestre) != semestre:
                    continue
                filtrados.append(course)
        elif user_rol == "estudiante":
            for course in cursos:
                if str(course.carrera) != carrera:
                    continue
                if semestre and str(course.semestre) != semestre:
                    continue
                filtrados.append(course)

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, course in enumerate(filtrados, 1):
            self.tree.insert(
                "",
                "end",
                values=(
                    idx,  # ID incremental
                    course.codigo,
                    course.nombre,
                    course.semestre,
                    course.carrera,
                    course.creditos,
                    course.requisitos,
                ),
            )
        self.current_courses = filtrados

    def on_carrera_selected(self, event=None):
        carrera = self.carrera_var.get()
        if "enfermería" in carrera.lower() or "enfermeria" in carrera.lower():
            semestres = [str(i) for i in range(1, 6)]
        elif "ingeniería" in carrera.lower() or "ingenieria" in carrera.lower():
            semestres = [str(i) for i in range(1, 10)]
        else:
            # Si no hay carrera seleccionada, muestra todos los semestres posibles
            semestres = sorted(
                {
                    str(course.semestre)
                    for course in self.course_controller.get_all()
                    if course.semestre is not None
                }
            )
        self.semestre_combo["values"] = [""] + semestres
        self.semestre_var.set("")  # Limpia la selección de semestre

    def search_courses(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.load_courses()
            return

        # Obtener todas las materias
        courses = self.course_controller.get_all()

        # Filtrar por coincidencia en código, nombre, carrera, semestre, créditos o requisitos
        filtered = []
        for course in courses:
            if (
                query in str(course.codigo).lower()
                or query in str(course.nombre).lower()
                or query in str(course.carrera or "").lower()
                or query in str(course.semestre or "").lower()
                or query in str(course.creditos or "").lower()
                or query in str(course.requisitos or "").lower()
            ):
                filtered.append(course)

        self.current_courses = filtered  # <-- NUEVO

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar resultados filtrados
        for idx, course in enumerate(filtered, 1):
            self.tree.insert(
                "",
                "end",
                values=(
                    idx,
                    course.codigo,
                    course.nombre,
                    course.semestre,
                    course.carrera,
                    course.creditos,
                    course.requisitos,
                ),
            )

    # def on_item_double_click(self, event):
    #     item = self.tree.identify_row(event.y)
    #     if item:
    #         self.edit_selected_course()

    # def edit_selected_course(self):
    #     selected = self.tree.selection()
    #     if not selected:
    #         messagebox.showwarning(
    #             "Advertencia", "Por favor, seleccione una materia para editar"
    #         )
    #         return

    #     item_id = self.tree.item(selected[0], "values")[0]
    #     self.show_edit_form(item_id)

    # def delete_selected_course(self):
    #     selected = self.tree.selection()
    #     if not selected:
    #         messagebox.showwarning(
    #             "Advertencia", "Por favor, seleccione una materia para eliminar"
    #         )
    #         return

    #     item_id = self.tree.item(selected[0], "values")[0]

    #     # Confirmar eliminación
    #     confirm = messagebox.askyesno(
    #         "Confirmar", "¿Está seguro de eliminar esta materia?"
    #     )
    #     if not confirm:
    #         return

    #     # Eliminar materia
    #     try:
    #         self.course_controller.delete(item_id)
    #         messagebox.showinfo("Éxito", "Materia eliminada correctamente")
    #         self.load_courses()
    #     except Exception as e:
    #         messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    # def show_add_form(self):
    #     # Implementación del formulario de agregar
    #     pass

    # def show_edit_form(self, course_id):
    #     # Implementación del formulario de edición
    #     pass
