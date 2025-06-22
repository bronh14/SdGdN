import tkinter as tk
from tkinter import ttk, messagebox
from config.database import (
    get_db_connection,
    get_periodo_activo,
    get_periodos_disponibles,
    set_periodo_activo,
)
from controllers.section_controller import SectionController
from controllers.course_controller import CourseController
from controllers.professor_controller import ProfessorController


class SectionListView:
    def __init__(self, parent, app_controller, user):
        self.parent = parent
        self.app_controller = app_controller
        self.user = user
        self.section_controller = SectionController()
        self.course_controller = CourseController()
        self.professor_controller = ProfessorController()
        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Gestión de Secciones",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Frame para el selector de período
        periodo_frame = tk.Frame(header_frame, bg="white")
        periodo_frame.pack(side="right", padx=10)

        tk.Label(periodo_frame, text="Período:", font=("Arial", 10), bg="white").pack(
            side="left", padx=5
        )
        self.periodo_var = tk.StringVar()
        self.periodo_cb = ttk.Combobox(
            periodo_frame, textvariable=self.periodo_var, state="readonly", width=10
        )
        self.periodo_cb.pack(side="left")

        # Cargar períodos disponibles
        periodos = get_periodos_disponibles()
        self.periodo_cb["values"] = [p[0] for p in periodos]

        # Establecer el período activo por defecto
        periodo_activo = get_periodo_activo()
        if periodo_activo:
            self.periodo_var.set(periodo_activo)
        elif periodos:
            self.periodo_var.set(periodos[0][0])

        # Botón para establecer período activo
        self.set_periodo_btn = tk.Button(
            periodo_frame,
            text="Establecer como activo",
            command=self.establecer_periodo_activo,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
        )
        self.set_periodo_btn.pack(side="left", padx=5)

        # Deshabilitar si ya hay un período activo al iniciar
        if periodo_activo:
            self.periodo_cb.config(state="disabled")
            self.set_periodo_btn.config(state="disabled")

        add_btn = tk.Button(
            header_frame,
            text="Agregar Nuevo",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.show_add_form,
        )
        add_btn.pack(side="right", padx=20, pady=15)

        # Contenido
        content_frame = tk.Frame(self.parent)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Frame para búsqueda
        search_frame = tk.Frame(content_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Buscar:", font=("Arial", 10)).pack(
            side="left", padx=5
        )
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.search_sections())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=5)

        # Tabla
        table_frame = tk.Frame(content_frame)
        table_frame.pack(fill="both", expand=True)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Scrollbar horizontal
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        # Treeview
        columns = (
            "id",
            "codigo",
            "materia",
            "seccion",
            "profesor",
            "aula",
            "capacidad",
            "estado",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )

        # Configurar scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configurar columnas
        headers = {
            "id": ("ID", 50),
            "codigo": ("Código", 100),
            "materia": ("Materia", 200),
            "seccion": ("Sección", 70),
            "profesor": ("Profesor", 180),
            "aula": ("Aula", 70),
            "capacidad": ("Capacidad", 70),
            "estado": ("Estado", 70),
        }

        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Botones de acción
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill="x", pady=10)

        edit_btn = tk.Button(
            action_frame,
            text="Editar",
            command=self.edit_selected_section,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        edit_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(
            action_frame,
            text="Eliminar",
            command=self.delete_selected_section,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        delete_btn.pack(side="left", padx=5)

        # Cargar secciones
        self.load_sections()

        # Configurar eventos
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def load_sections(self):
        """Carga las secciones del período seleccionado"""
        periodo = self.periodo_var.get()
        if not periodo:
            return

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
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
                        s.estado
                    FROM secciones s
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN profesores p ON s.id_profesor = p.id_profesor
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE s.periodo = ?
                    ORDER BY m.codigo, s.numero_seccion
                """,
                    (periodo,),
                )

                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar secciones: {str(e)}")

    def search_sections(self):
        query = self.search_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        sections = self.section_controller.get_all()
        for section in sections:
            if any(query in str(field).lower() for field in section):
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        section[0],
                        section[1],
                        section[2],
                        f"D{section[3]}" if section[3] else "N/A",
                        section[4],
                        section[5],
                        section[6],
                        section[7],
                    ),
                )

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.edit_selected_section()

    def edit_selected_section(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione una sección para editar"
            )
            return

        item_id = self.tree.item(selected[0], "values")[0]
        self.show_edit_form(item_id)

    def delete_selected_section(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione una sección para eliminar"
            )
            return

        item_id = self.tree.item(selected[0], "values")[0]
        confirm = messagebox.askyesno(
            "Confirmar", "¿Está seguro de eliminar esta sección?"
        )
        if not confirm:
            return

        try:
            self.section_controller.delete(item_id)
            messagebox.showinfo("Éxito", "Sección eliminada correctamente")
            self.load_sections()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def show_add_form(self):
        """Muestra el formulario para agregar una nueva sección"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Nueva Sección")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()

        # Centrar el diálogo
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = 500
        dialog_height = 600
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        # Título
        tk.Label(
            form_frame,
            text="Nueva Sección",
            font=("Arial", 14, "bold"),
        ).pack(pady=(0, 20))

        # Período
        tk.Label(form_frame, text="Período:", font=("Arial", 10)).pack(anchor="w")
        periodo_var = tk.StringVar()
        periodo_cb = ttk.Combobox(
            form_frame, textvariable=periodo_var, state="readonly", width=20
        )
        periodo_cb.pack(fill="x", pady=(0, 10))

        # Cargar períodos disponibles
        periodos = get_periodos_disponibles()
        periodo_cb["values"] = [p[0] for p in periodos]

        # Establecer el período activo por defecto
        periodo_activo = get_periodo_activo()
        if periodo_activo:
            periodo_var.set(periodo_activo)
        elif periodos:
            periodo_var.set(periodos[0][0])

        # Si el usuario es coordinador, deshabilitar el selector de periodo
        if hasattr(self.user, "rol") and self.user.rol == "coordinacion":
            periodo_cb.config(state="disabled")

        # Semestre
        tk.Label(form_frame, text="Semestre:", font=("Arial", 10)).pack(anchor="w")
        semestre_var = tk.IntVar(value=1)
        semestre_cb = ttk.Combobox(
            form_frame, textvariable=semestre_var, state="readonly", width=20
        )
        semestre_cb.pack(fill="x", pady=(0, 10))

        # Obtener la carrera del coordinador
        def get_carrera_coordinador():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT carrera 
                    FROM coordinadores 
                    WHERE id_usuario = ?
                """,
                    (self.user.id,),
                )
                result = cursor.fetchone()
                return result[0] if result else None

        carrera = get_carrera_coordinador()
        if carrera == "Enfermería":
            semestres = list(range(1, 6))
        else:
            semestres = list(range(1, 10))
        semestre_cb["values"] = semestres

        # Materia
        tk.Label(form_frame, text="Materia:", font=("Arial", 10)).pack(anchor="w")
        materia_var = tk.StringVar()
        materia_cb = ttk.Combobox(
            form_frame, textvariable=materia_var, state="readonly", width=20
        )
        materia_cb.pack(fill="x", pady=(0, 10))

        def update_materias(*args):
            """Actualiza la lista de materias según el semestre seleccionado"""
            semestre = semestre_var.get()
            if not semestre:
                return

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id_materia, nombre 
                    FROM materias 
                    WHERE semestre = ? AND carrera = ?
                    ORDER BY nombre
                """,
                    (semestre, carrera),
                )
                materias = cursor.fetchall()
                materia_cb["values"] = [f"{m[0]} - {m[1]}" for m in materias]
                if materias:
                    materia_var.set(f"{materias[0][0]} - {materias[0][1]}")
                else:
                    materia_var.set("")

        # Vincular el cambio de semestre con la actualización de materias
        semestre_var.trace("w", update_materias)
        # Cargar materias iniciales
        update_materias()

        # Número de sección
        tk.Label(form_frame, text="Número de Sección:", font=("Arial", 10)).pack(
            anchor="w"
        )
        numero_var = tk.IntVar(value=1)
        numero_cb = ttk.Combobox(
            form_frame,
            textvariable=numero_var,
            values=[1, 2, 3],
            state="readonly",
            width=20,
        )
        numero_cb.pack(fill="x", pady=(0, 10))

        # Profesor
        tk.Label(form_frame, text="Profesor:", font=("Arial", 10)).pack(anchor="w")
        profesor_var = tk.StringVar()
        profesor_cb = ttk.Combobox(
            form_frame, textvariable=profesor_var, state="readonly", width=20
        )
        profesor_cb.pack(fill="x", pady=(0, 10))

        # Cargar profesores
        profesores = self.section_controller.get_profesores()
        profesor_cb["values"] = [f"{p[0]} - {p[1]}" for p in profesores]

        # Aula
        tk.Label(form_frame, text="Aula:", font=("Arial", 10)).pack(anchor="w")
        aula_var = tk.StringVar()
        aula_entry = ttk.Entry(form_frame, textvariable=aula_var, width=20)
        aula_entry.pack(fill="x", pady=(0, 10))

        # Capacidad
        tk.Label(form_frame, text="Capacidad:", font=("Arial", 10)).pack(anchor="w")
        capacidad_var = tk.StringVar(value="30")
        capacidad_entry = ttk.Entry(form_frame, textvariable=capacidad_var, width=20)
        capacidad_entry.pack(fill="x", pady=(0, 10))

        # Estado
        tk.Label(form_frame, text="Estado:", font=("Arial", 10)).pack(anchor="w")
        estado_var = tk.StringVar(value="activa")
        estado_cb = ttk.Combobox(
            form_frame,
            textvariable=estado_var,
            values=["activa", "inactiva"],
            state="readonly",
            width=20,
        )
        estado_cb.pack(fill="x", pady=(0, 20))

        def submit():
            try:
                # Validar campos requeridos
                if not all([periodo_var.get(), materia_var.get(), numero_var.get()]):
                    messagebox.showerror(
                        "Error", "Todos los campos marcados con * son obligatorios."
                    )
                    return

                # Obtener ID de la materia
                materia_id = int(materia_var.get().split(" - ")[0])

                # Obtener ID del profesor si se seleccionó uno
                profesor_id = None
                if profesor_var.get():
                    profesor_id = int(profesor_var.get().split(" - ")[0])

                # Crear la sección
                self.section_controller.create_section(
                    materia_id=materia_id,
                    numero_seccion=numero_var.get(),
                    id_profesor=profesor_id,
                    periodo=periodo_var.get(),
                    aula=aula_var.get() or None,
                    capacidad=int(capacidad_var.get()),
                    estado=estado_var.get(),
                )

                messagebox.showinfo("Éxito", "Sección creada exitosamente.")
                dialog.destroy()
                self.load_sections()

            except Exception as e:
                messagebox.showerror("Error", f"Error al crear la sección: {str(e)}")

        # Botones
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        submit_btn = tk.Button(
            button_frame,
            text="Guardar",
            command=submit,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        submit_btn.pack(side="right", padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        cancel_btn.pack(side="right", padx=5)

    def show_edit_form(self, section_id):
        """Muestra el formulario para editar una sección existente"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Editar Sección")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()

        # Centrar el diálogo
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = 500
        dialog_height = 600
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        # Título
        tk.Label(
            form_frame,
            text="Editar Sección",
            font=("Arial", 14, "bold"),
        ).pack(pady=(0, 20))

        # Obtener datos de la sección
        section_data = self.section_controller.get_section(section_id)
        if not section_data:
            messagebox.showerror("Error", "No se encontró la sección.")
            dialog.destroy()
            return

        # Período
        tk.Label(form_frame, text="Período:", font=("Arial", 10)).pack(anchor="w")
        periodo_var = tk.StringVar(value=section_data["periodo"])
        periodo_cb = ttk.Combobox(
            form_frame, textvariable=periodo_var, state="readonly", width=20
        )
        periodo_cb.pack(fill="x", pady=(0, 10))

        # Cargar períodos disponibles
        periodos = get_periodos_disponibles()
        periodo_cb["values"] = [p[0] for p in periodos]

        # Materia
        tk.Label(form_frame, text="Materia:", font=("Arial", 10)).pack(anchor="w")
        materia_var = tk.StringVar(
            value=f"{section_data['id_materia']} - {section_data['nombre_materia']}"
        )
        materia_cb = ttk.Combobox(
            form_frame, textvariable=materia_var, state="readonly", width=20
        )
        materia_cb.pack(fill="x", pady=(0, 10))

        # Cargar materias
        materias = self.section_controller.get_materias()
        materia_cb["values"] = [f"{m[0]} - {m[1]}" for m in materias]

        # Número de sección
        tk.Label(form_frame, text="Número de Sección:", font=("Arial", 10)).pack(
            anchor="w"
        )
        numero_var = tk.IntVar(value=section_data["numero_seccion"])
        numero_cb = ttk.Combobox(
            form_frame,
            textvariable=numero_var,
            values=[1, 2, 3],
            state="readonly",
            width=20,
        )
        numero_cb.pack(fill="x", pady=(0, 10))

        # Profesor
        tk.Label(form_frame, text="Profesor:", font=("Arial", 10)).pack(anchor="w")
        profesor_var = tk.StringVar()
        if section_data["id_profesor"]:
            profesor_var.set(
                f"{section_data['id_profesor']} - {section_data['nombre_profesor']}"
            )
        profesor_cb = ttk.Combobox(
            form_frame, textvariable=profesor_var, state="readonly", width=20
        )
        profesor_cb.pack(fill="x", pady=(0, 10))

        # Cargar profesores
        profesores = self.section_controller.get_profesores()
        profesor_cb["values"] = [f"{p[0]} - {p[1]}" for p in profesores]

        # Aula
        tk.Label(form_frame, text="Aula:", font=("Arial", 10)).pack(anchor="w")
        aula_var = tk.StringVar(value=section_data["aula"] or "")
        aula_entry = ttk.Entry(form_frame, textvariable=aula_var, width=20)
        aula_entry.pack(fill="x", pady=(0, 10))

        # Capacidad
        tk.Label(form_frame, text="Capacidad:", font=("Arial", 10)).pack(anchor="w")
        capacidad_var = tk.StringVar(value=str(section_data["capacidad"]))
        capacidad_entry = ttk.Entry(form_frame, textvariable=capacidad_var, width=20)
        capacidad_entry.pack(fill="x", pady=(0, 10))

        # Estado
        tk.Label(form_frame, text="Estado:", font=("Arial", 10)).pack(anchor="w")
        estado_var = tk.StringVar(value=section_data["estado"])
        estado_cb = ttk.Combobox(
            form_frame,
            textvariable=estado_var,
            values=["activa", "inactiva"],
            state="readonly",
            width=20,
        )
        estado_cb.pack(fill="x", pady=(0, 20))

        def submit():
            try:
                # Validar campos requeridos
                if not all([periodo_var.get(), materia_var.get(), numero_var.get()]):
                    messagebox.showerror(
                        "Error", "Todos los campos marcados con * son obligatorios."
                    )
                    return

                # Obtener ID de la materia
                materia_id = int(materia_var.get().split(" - ")[0])

                # Obtener ID del profesor si se seleccionó uno
                profesor_id = None
                if profesor_var.get():
                    profesor_id = int(profesor_var.get().split(" - ")[0])

                # Actualizar la sección
                self.section_controller.update_section(
                    section_id=section_id,
                    materia_id=materia_id,
                    numero_seccion=numero_var.get(),
                    id_profesor=profesor_id,
                    periodo=periodo_var.get(),
                    aula=aula_var.get() or None,
                    capacidad=int(capacidad_var.get()),
                    estado=estado_var.get(),
                )

                messagebox.showinfo("Éxito", "Sección actualizada exitosamente.")
                dialog.destroy()
                self.load_sections()

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al actualizar la sección: {str(e)}"
                )

        # Botones
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        submit_btn = tk.Button(
            button_frame,
            text="Guardar",
            command=submit,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        submit_btn.pack(side="right", padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        cancel_btn.pack(side="right", padx=5)

    def establecer_periodo_activo(self):
        """Establece el período seleccionado como activo"""
        periodo = self.periodo_var.get()
        if periodo:
            try:
                set_periodo_activo(periodo)
                messagebox.showinfo(
                    "Éxito", f"Período {periodo} establecido como activo."
                )
                self.load_sections()
                # Deshabilitar el selector de período y el botón
                self.periodo_cb.config(state="disabled")
                self.set_periodo_btn.config(state="disabled")
                self.parent.update_idletasks()  # Forzar la actualización de la interfaz
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al establecer período activo: {str(e)}"
                )
