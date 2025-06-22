import tkinter as tk
from tkinter import ttk, messagebox
from controllers.student_controller import StudentController
from controllers.user_controller import UserController
from config.inscripcion import set_inscripcion_habilitada, get_inscripcion_habilitada


class StudentListView:
    def __init__(self, parent, app_controller, user):
        self.parent = parent
        self.app_controller = app_controller
        self.user = user
        self.student_controller = StudentController()
        self.user_controller = UserController()

        # Crear interfaz
        self.create_widgets()

    def activar_desactivar_inscripcion(self):
        estado_actual = get_inscripcion_habilitada()
        set_inscripcion_habilitada(not estado_actual)
        nuevo_estado = "habilitada" if not estado_actual else "deshabilitada"
        messagebox.showinfo("Inscripción", f"La inscripción ha sido {nuevo_estado}.")

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Gestión de Estudiantes",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        add_btn = tk.Button(
            header_frame,
            text="Habilitar/Deshabilitar Inscripción",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.activar_desactivar_inscripcion,
        )
        add_btn.pack(side="right", padx=20, pady=15)

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
            command=self.search_students,
        )
        search_btn.pack(side="left", padx=10)

        # Tabla
        table_frame = tk.Frame(content_container, bg="white")
        table_frame.pack(fill="both", expand=True)

        # Configurar columnas
        columns = (
            # "id",
            "cedula",
            "nombre",
            "apellido",
            "carrera",
            "semestre",
            "fecha_ingreso",
        )

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
        self.load_students()

        # Menú contextual
        self.tree.bind("<Double-1>", self.on_item_double_click)

        # Botones de acción
        action_frame = tk.Frame(content_container, bg="#f5f5f5", pady=10)
        action_frame.pack(fill="x")

        edit_btn = tk.Button(
            action_frame,
            text="Editar",
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.edit_selected_student,
        )
        edit_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(
            action_frame,
            text="Eliminar",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.delete_selected_student,
        )
        delete_btn.pack(side="left", padx=5)

        refresh_btn = tk.Button(
            action_frame,
            text="Actualizar",
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.load_students,
        )
        refresh_btn.pack(side="left", padx=5)

    def load_students(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener estudiantes
        students = self.student_controller.get_all()

        # Insertar datos en la tabla
        for student in students:
            self.tree.insert("", "end", values=student[1:])

    def search_students(self):
        query = self.search_entry.get().lower()
        students = self.student_controller.get_all()
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Filtrar resultados
        for student in students:
            # Convierte todos los campos a string y busca coincidencia parcial
            if any(query in str(field).lower() for field in student[1:]):
                self.tree.insert("", "end", values=student[1:])

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.edit_selected_student()

    def edit_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un estudiante para editar"
            )
            return

        cedula = self.tree.item(selected[0], "values")[0]

        student_id = self.student_controller.get_id_by_cedula(cedula)

        if not student_id:
            messagebox.showerror("Error", "No se encontró el coordinador por cédula")
            return

        self.show_edit_form(student_id)

    def delete_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un estudiante para eliminar"
            )
            return

        cedula = self.tree.item(selected[0], "values")[0]

        # Confirmar eliminación
        confirm = messagebox.askyesno(
            "Confirmar", "¿Está seguro de eliminar este estudiante?"
        )

        if not confirm:
            return

        student_id = self.student_controller.get_id_by_cedula(cedula)

        if not student_id:
            messagebox.showerror("Error", "No se encontró el estudiante por cédula")
            return

        # Eliminar estudiante
        try:
            self.student_controller.delete(student_id)
            messagebox.showinfo("Éxito", "Estudiante eliminado correctamente")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def show_edit_form(self, student_id):
        # Buscar datos actuales
        students = self.student_controller.get_all()
        data = None
        for s in students:
            if str(s[0]) == str(student_id):
                data = s
                break
        if not data:
            messagebox.showerror("Error", "Estudiante no encontrado")
            return

        form = tk.Toplevel(self.parent)
        form.title("Editar Estudiante")
        form.geometry("380x270")
        form.transient(self.parent)
        form.grab_set()

        labels = ["Cédula", "Nombre", "Apellido", "Carrera", "Semestre"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=("Arial", 12)).grid(
                row=i, column=0, pady=8, padx=10, sticky="w"
            )
            entry = tk.Entry(form, font=("Arial", 12), width=28)
            entry.grid(row=i, column=1, pady=8, padx=10)
            entry.insert(0, str(data[i + 1]))  # data[0]=id, data[1]=cedula, etc.
            entries.append(entry)

        def submit():
            cedula = entries[0].get()
            nombre = entries[1].get().title()
            apellido = entries[2].get().title()
            carrera = entries[3].get()
            semestre = entries[4].get()

            # Validar campos vacíos
            if not cedula or not nombre or not apellido or not carrera or not semestre:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            try:
                # Llama al controlador para actualizar ambos: usuario y estudiante
                self.student_controller.update(
                    student_id,
                    cedula=cedula,
                    nombre=nombre,
                    apellido=apellido,
                    carrera=carrera,
                    semestre=semestre,
                )
                messagebox.showinfo("Éxito", "Estudiante actualizado correctamente")
                form.destroy()
                self.load_students()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")

        btn = tk.Button(
            form,
            text="Guardar Cambios",
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            command=submit,
        )
        btn.grid(row=len(labels), column=0, columnspan=2, pady=20)
