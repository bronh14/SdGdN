from datetime import datetime
import tkinter as tk
from config.database import get_carreras, get_db_connection
from tkinter import ttk, messagebox, filedialog
from controllers.professor_controller import ProfessorController
from controllers.user_controller import UserController
from controllers.section_controller import SectionController
from controllers.grade_controller import GradeController
from models.professor import Professor
from tkcalendar import DateEntry
from pdf import reportesPDF


class ProfessorListView:
    def __init__(self, parent, app_controller, user):
        self.parent = parent
        self.app_controller = app_controller
        self.user = user
        self.professor_controller = ProfessorController()
        self.user_controller = UserController()

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Gestión de Profesores",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Botón para Crear
        add_btn = tk.Button(
            header_frame,
            text="Agregar Profesor",
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
            command=self.search_professors,
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
            "fecha_contratacion",
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
        self.load_professors()

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
            command=self.edit_selected_professor,
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
            command=self.delete_selected_professor,
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
            command=self.load_professors,
        )
        refresh_btn.pack(side="left", padx=5)

    def load_professors(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filtrar profesores según el usuario
        if self.user.id == 1:  # Admin ve todos
            professors = self.professor_controller.get_all()
        elif self.user.rol == "coordinacion":
            # Obtener la carrera del coordinador
            carrera = self.get_coordinator_carrera(self.user.id)
            professors = [
                p for p in self.professor_controller.get_all() if p[4] == carrera
            ]
        else:
            professors = []

        # Insertar datos en la tabla
        for professor in professors:
            self.tree.insert("", "end", values=professor[1:])

    def get_coordinator_carrera(self, user_id):
        # Busca la carrera del coordinador en la tabla coordinadores
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT carrera FROM coordinadores WHERE id_usuario = ?", (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def search_professors(self):
        query = self.search_entry.get().lower()
        professors = self.professor_controller.get_all()
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Filtrar resultados
        for professor in professors:
            if any(query in str(field).lower() for field in professor[1:]):
                self.tree.insert("", "end", values=professor[1:])

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.edit_selected_professor()

    def edit_selected_professor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un profesor para editar"
            )
            return

        cedula = self.tree.item(selected[0], "values")[0]
        professor_id = self.professor_controller.get_id_by_cedula(cedula)
        if not professor_id:
            messagebox.showerror("Error", "No se encontró el coordinador por cédula")
            return
        self.show_edit_form(professor_id)

    def delete_selected_professor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un profesor para eliminar"
            )
            return

        cedula = self.tree.item(selected[0], "values")[0]

        # Confirmar eliminación
        confirm = messagebox.askyesno(
            "Confirmar", "¿Está seguro de eliminar este profesor?"
        )

        if not confirm:
            return

        professor_id = self.professor_controller.get_id_by_cedula(cedula)

        if not professor_id:
            messagebox.showerror("Error", "No se encontró el profesor por cédula")
            return

        # Eliminar profesor
        try:
            self.professor_controller.delete(professor_id)
            messagebox.showinfo("Éxito", "Profesor eliminado correctamente")
            self.load_professors()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def show_add_form(self):
        form = tk.Toplevel(self.parent)

        form.title("Agregar Profesor")
        form.geometry("560x310")
        form.transient(self.parent)
        form.grab_set()

        labels = [
            "Cédula",
            "Nombre",
            "Apellido",
            "Carrera",
            "Fecha Contratación (YYYY-MM-DD)",
        ]
        entries = []
        carreras = get_carreras()
        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=("Arial", 12)).grid(
                row=i, column=0, pady=8, padx=10, sticky="w"
            )
            if label == "Carrera":
                carrera_combo = ttk.Combobox(
                    form,
                    values=carreras,
                    font=("Arial", 12),
                    width=26,
                    state="readonly",
                )
                carrera_combo.grid(row=i, column=1, pady=8, padx=10)
                entries.append(carrera_combo)
            elif (
                label == "Fecha de Contratación (YYYY-MM-DD)"
                or label == "Fecha Contratación (YYYY-MM-DD)"
            ):
                fecha_entry = DateEntry(
                    form,
                    font=("Arial", 12),
                    width=26,
                    date_pattern="yyyy-mm-dd",  # Formato compatible con tu base de datos
                    background="#2980b9",
                    foreground="white",
                    borderwidth=2,
                    showweeknumbers=False,
                )
                fecha_entry.grid(row=i, column=1, pady=8, padx=10)
                entries.append(fecha_entry)
            else:
                entry = tk.Entry(form, font=("Arial", 12), width=28)
                entry.grid(row=i, column=1, pady=8, padx=10)
                entries.append(entry)

        def submit():
            cedula = entries[0].get()
            nombre = entries[1].get().title()
            apellido = entries[2].get().title()
            carrera = entries[3].get()
            fecha_contratacion = entries[4].get()

            # Validar campos vacíos
            if (
                not cedula
                or not nombre
                or not apellido
                or not carrera
                or not fecha_contratacion
            ):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            # Validar fecha
            try:
                datetime.strptime(fecha_contratacion, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha incorrecto. Use YYYY-MM-DD"
                )
                return

            try:
                self.professor_controller.create(
                    cedula,
                    nombre,
                    apellido,
                    carrera,
                    fecha_contratacion,
                )
                messagebox.showinfo("Éxito", "Profesor creado correctamente")
                form.destroy()
                self.load_professors()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear: {str(e)}")

        btn = tk.Button(
            form,
            text="Guardar",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            command=submit,
        )
        btn.grid(row=len(labels), column=0, columnspan=2, pady=20)

    def show_edit_form(self, professor_id):

        professors = self.professor_controller.get_all()
        data = None
        for p in professors:
            if str(p[0]) == str(professor_id):
                data = p
                break
        if not data:
            messagebox.showerror("Error", "Profesor no encontrado")
            return

        form = tk.Toplevel(self.parent)
        form.title("Editar Profesor")
        form.geometry("560x310")
        form.transient(self.parent)
        form.grab_set()

        labels = [
            "Cédula",
            "Nombre",
            "Apellido",
            "Carrera",
            "Fecha Contratación (YYYY-MM-DD)",
        ]
        entries = []
        carreras = get_carreras()
        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=("Arial", 12)).grid(
                row=i, column=0, pady=8, padx=10, sticky="w"
            )
            if label == "Carrera":
                carrera_combo = ttk.Combobox(
                    form,
                    values=carreras,
                    font=("Arial", 12),
                    width=26,
                    state="readonly",
                )
                carrera_combo.grid(row=i, column=1, pady=8, padx=10)
                carrera_combo.set(data[i + 1])
                entries.append(carrera_combo)
            elif (
                label == "Fecha de Contratación (YYYY-MM-DD)"
                or label == "Fecha Contratación (YYYY-MM-DD)"
            ):
                fecha_entry = DateEntry(
                    form,
                    font=("Arial", 12),
                    width=26,
                    date_pattern="yyyy-mm-dd",
                    background="#2980b9",
                    foreground="white",
                    borderwidth=2,
                    showweeknumbers=False,
                )
                # Pre-cargar la fecha existente
                try:
                    fecha_entry.set_date(datetime.strptime(data[i + 1], "%Y-%m-%d"))
                except Exception:
                    pass
                fecha_entry.grid(row=i, column=1, pady=8, padx=10)
                entries.append(fecha_entry)
            else:
                entry = tk.Entry(form, font=("Arial", 12), width=28)
                entry.grid(row=i, column=1, pady=8, padx=10)
                entry.insert(0, data[i + 1])
                entries.append(entry)

        def submit():
            cedula = entries[0].get()
            nombre = entries[1].get().title()
            apellido = entries[2].get().title()
            carrera = entries[3].get()
            fecha_contratacion = entries[4].get()

            # Validar campos vacíos
            if (
                not cedula
                or not nombre
                or not apellido
                or not carrera
                or not fecha_contratacion
            ):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            # Validar fecha
            try:
                datetime.strptime(fecha_contratacion, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha incorrecto. Use YYYY-MM-DD"
                )
                return

            try:
                self.professor_controller.update(
                    professor_id,
                    cedula,
                    nombre,
                    apellido,
                    carrera,
                    fecha_contratacion,
                )
                messagebox.showinfo("Éxito", "Profesor actualizado correctamente")
                form.destroy()
                self.load_professors()
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


class GestionNotasProfesorView:
    def __init__(self, parent, user):
        import tkinter as tk
        from tkinter import ttk
        from models.professor import Professor

        self.parent = parent
        self.user = user
        self.professor = Professor.get_by_user_id(user.id)
        self.section_controller = SectionController()
        self.grade_controller = GradeController()
        self.setup_ui()

    def setup_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        import tkinter as tk
        from tkinter import ttk

        tk.Label(self.parent, text="Materia:", font=("Arial", 12)).pack(
            anchor="w", padx=20, pady=(10, 0)
        )

        # Frame para materia y botón PDF
        materia_frame = tk.Frame(self.parent)
        materia_frame.pack(anchor="w", padx=20, pady=(0, 10), fill="x")

        self.materia_var = tk.StringVar()
        self.materia_cb = ttk.Combobox(
            materia_frame, textvariable=self.materia_var, state="readonly", width=40
        )
        self.materia_cb.pack(side="left", padx=(0, 10))

        # Botón para generar PDF
        pdf_btn = tk.Button(
            materia_frame,
            text="Generar PDF de Notas",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.generar_pdf_notas,
        )
        pdf_btn.pack(side="right")

        # Cargar materias del profesor
        if not self.professor:
            messagebox.showerror(
                "Error de Usuario",
                "No se encontró el perfil de profesor para el usuario actual.",
            )
            for widget in self.parent.winfo_children():
                widget.destroy()
            tk.Label(
                self.parent,
                text="Error al cargar el perfil del profesor.",
                font=("Arial", 14, "bold"),
            ).pack(pady=50)
            return
        secciones = self.section_controller.get_by_professor(self.professor.id)
        self.materias_map = {}
        materias_display = []
        for s in secciones:
            # Ajusta los índices según la estructura real de 's'
            # Ejemplo: (nombre_materia, periodo, aula, seccion, estudiantes, id_seccion)
            if len(s) >= 6:
                display = f"{s[0]} (Sección {s[3]}, {s[1]})"
                materias_display.append(display)
                self.materias_map[display] = (s[5], s[0])  # id_seccion, nombre_materia
            else:
                # Si la tupla es más corta, ignora o ajusta según lo que tengas
                continue

        self.materia_cb["values"] = materias_display
        self.materia_cb.bind("<<ComboboxSelected>>", self.cargar_estudiantes)

        columns = (
            "nro",
            "ci",
            "nombres",
            "apellidos",
            "corte1",
            "corte2",
            "corte3",
            "corte4",
            "nota_def",
        )
        self.tree = ttk.Treeview(
            self.parent, columns=columns, show="headings", height=15
        )
        for col, txt, w in zip(
            columns,
            [
                "Nº",
                "C.I",
                "NOMBRES",
                "APELLIDOS",
                "CORTE 1 (25%)",
                "CORTE 2 (25%)",
                "CORTE 3 (25%)",
                "CORTE 4 (25%)",
                "NOTA DEF.",
            ],
            [40, 100, 150, 150, 90, 90, 90, 90, 90],
        ):
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        # Identificar la celda
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_num = int(col.replace("#", "")) - 1  # 0-indexed

        # Solo permitir edición en columnas de cortes (índices 4,5,6,7)
        if col_num not in [4, 5, 6, 7]:
            return

        x, y, width, height = self.tree.bbox(item_id, col)
        value = self.tree.set(item_id, self.tree["columns"][col_num])

        # Crear Entry para editar
        entry = tk.Entry(self.tree, width=6)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            new_value = entry.get()
            # Validar que sea número
            try:
                nota = float(new_value)
                if nota < 0 or nota > 20:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "La nota debe ser un número entre 0 y 20")
                entry.destroy()
                return

            self.tree.set(item_id, self.tree["columns"][col_num], new_value)
            entry.destroy()

            # Guardar en la base de datos
            self.guardar_nota(item_id, col_num, nota)

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def guardar_nota(self, item_id, col_num, nota):
        # Obtener datos del estudiante y sección
        values = self.tree.item(item_id, "values")
        ci = values[1]
        display = self.materia_var.get()
        id_seccion, _ = self.materias_map[display]

        # Buscar la inscripción del estudiante en la sección
        from models.enrollment import Enrollment

        inscripciones = Enrollment.get_by_section(id_seccion)
        inscripcion_id = None
        for ins in inscripciones:
            if str(ins[1]) == str(ci):  # ins[1] es la cédula
                inscripcion_id = ins[0]  # ins[0] es id_inscripcion
                break

        if not inscripcion_id:
            messagebox.showerror(
                "Error", "No se encontró la inscripción del estudiante."
            )
            return

        # Determinar el tipo de corte
        corte_map = {4: "corte1", 5: "corte2", 6: "corte3", 7: "corte4"}
        tipo_evaluacion = corte_map.get(col_num, "corte1")

        # Guardar o actualizar la nota
        from models.grade import Grade

        Grade.save_or_update(inscripcion_id, tipo_evaluacion, nota)
        messagebox.showinfo("Éxito", f"Nota guardada para {tipo_evaluacion.upper()}.")

        # Recalcular nota definitiva
        values = list(self.tree.item(item_id, "values"))
        try:
            # Asegurarse de que los valores no estén vacíos antes de convertirlos
            cortes = [float(v) for v in values[4:8] if v]
        except (ValueError, IndexError):
            cortes = []  # Si hay un error, la lista de cortes estará vacía

        # Calcular la nota solo si hay notas válidas
        nota_def = round(sum(cortes) / 4, 2) if cortes else 0.0
        values[8] = str(nota_def)  # índice 8 es la columna NOTA DEF.
        self.tree.item(item_id, values=values)

        # Guardar nota definitiva en la base de datos
        ci = values[1]
        display = self.materia_var.get()
        id_seccion, _ = self.materias_map[display]

        from models.enrollment import Enrollment

        inscripciones = Enrollment.get_by_section(id_seccion)
        inscripcion_id = None
        for ins in inscripciones:
            if str(ins[1]) == str(ci):  # ins[1] es la cédula
                inscripcion_id = ins[0]  # ins[0] es id_inscripcion
                break

        if inscripcion_id:
            from models.grade import Grade

            Grade.save_or_update(inscripcion_id, "nota_def", nota_def)

    def cargar_estudiantes(self, event=None):
        # Limpia la tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        display = self.materia_var.get()
        if not display or display not in self.materias_map:
            return

        id_seccion, _ = self.materias_map[display]

        from models.enrollment import Enrollment
        from models.grade import Grade

        inscripciones = Enrollment.get_by_section(id_seccion)
        estudiantes = []
        for ins in inscripciones:
            inscripcion_id = ins[0]
            ci = ins[1]
            nombres = ins[2]
            apellidos = ins[3]

            # Obtener notas de la base de datos
            notas = {"corte1": 0, "corte2": 0, "corte3": 0, "corte4": 0, "nota_def": 0}
            calificaciones = Grade.get_by_inscripcion(inscripcion_id)
            for cal in calificaciones:
                notas[cal.tipo_evaluacion] = cal.valor_nota

            estudiantes.append(
                (
                    ci,
                    nombres,
                    apellidos,
                    notas.get("corte1", 0),
                    notas.get("corte2", 0),
                    notas.get("corte3", 0),
                    notas.get("corte4", 0),
                    notas.get("nota_def", 0),
                )
            )

        for idx, est in enumerate(estudiantes, start=1):
            self.tree.insert(
                "",
                "end",
                values=(
                    idx,
                    est[0],  # C.I
                    est[1],  # Nombres
                    est[2],  # Apellidos
                    est[3],  # Corte 1
                    est[4],  # Corte 2
                    est[5],  # Corte 3
                    est[6],  # Corte 4
                    est[7],  # Nota Def.
                ),
            )

    def generar_pdf_notas(self):
        # Verificar que se haya seleccionado una materia
        display = self.materia_var.get()
        if not display or display not in self.materias_map:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione una materia primero"
            )
            return

        try:
            # Abrir diálogo para guardar archivo
            file_path = filedialog.asksaveasfilename(
                initialfile=f"notas_{display.split(' (')[0].replace(' ', '_').upper()}.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar Reporte de Notas como PDF",
            )
            if not file_path:
                return  # El usuario canceló

            # Obtener datos de la materia seleccionada
            id_seccion, nombre_materia = self.materias_map[display]

            # Obtener información de la sección
            seccion_info = self.section_controller.get_by_id(id_seccion)
            if not seccion_info:
                messagebox.showerror(
                    "Error", "No se encontró información de la sección"
                )
                return

            # Obtener estudiantes y sus notas
            from models.enrollment import Enrollment
            from models.grade import Grade

            inscripciones = Enrollment.get_by_section(id_seccion)
            estudiantes_notas = []

            for ins in inscripciones:
                inscripcion_id = ins[0]
                ci = ins[1]
                nombres = ins[2]
                apellidos = ins[3]

                # Obtener notas de la base de datos
                notas = {
                    "corte1": 0,
                    "corte2": 0,
                    "corte3": 0,
                    "corte4": 0,
                    "nota_def": 0,
                }
                calificaciones = Grade.get_by_inscripcion(inscripcion_id)
                for cal in calificaciones:
                    notas[cal.tipo_evaluacion] = cal.valor_nota

                estudiantes_notas.append(
                    {
                        "ci": ci,
                        "nombres": nombres,
                        "apellidos": apellidos,
                        "corte1": notas.get("corte1", 0),
                        "corte2": notas.get("corte2", 0),
                        "corte3": notas.get("corte3", 0),
                        "corte4": notas.get("corte4", 0),
                        "nota_def": notas.get("nota_def", 0),
                    }
                )

            # Generar el PDF usando la función del módulo reportesPDF
            reportesPDF.generar_reporte_notas_profesor(
                file_path,
                estudiantes_notas,
                nombre_materia,
                display,
                self.user.nombre,
                self.user.apellido,
                seccion_info,
            )

            messagebox.showinfo(
                "Éxito", "El reporte de notas se exportó correctamente a PDF."
            )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte a PDF:\n{e}")
