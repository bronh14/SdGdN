from datetime import datetime
import tkinter as tk
from config.database import get_carreras,get_db_connection, set_periodo_activo,get_periodo_activo
from tkinter import ttk, messagebox
from controllers.coordinator_controller import CoordinatorController
from controllers.user_controller import UserController
from tkcalendar import DateEntry

class CoordinatorListView:

    def __init__(self, parent, app_controller, user):
        self.parent = parent
        self.app_controller = app_controller
        self.user = user
        self.user_controller = UserController()
        self.coordinator_controller = CoordinatorController()  # <-- Agrega esto
        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Gestión de Coordinadores",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        add_btn = tk.Button(
            header_frame,
            text="Agregar Coordinador",
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
            command=self.search_coordinators,
        )
        search_btn.pack(side="left", padx=10)

        # Tabla
        table_frame = tk.Frame(content_container, bg="white")
        table_frame.pack(fill="both", expand=True)

        columns = (
            # "id",
            "cedula",
            "nombre",
            "apellido",
            "departamento",
            "fecha_ingreso",
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="center")

        self.load_coordinators()
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
            command=self.edit_selected_coordinator,
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
            command=self.delete_selected_coordinator,
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
            command=self.load_coordinators,
        )
        refresh_btn.pack(side="left", padx=5)

        close_period_btn = tk.Button(
            header_frame,
            text="Cerrar Período Académico",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.cerrar_periodo_academico,
        )
        close_period_btn.pack(side="right", padx=10, pady=15)

    def load_coordinators(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        coordinators = self.coordinator_controller.get_all()

        for coordinator in coordinators:
            self.tree.insert("", "end", values=coordinator[1:])

    def search_coordinators(self):
        query = self.search_entry.get().lower()
        coordinators = self.coordinator_controller.get_all()
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Filtrar resultados
        for coordinator in coordinators:
            if any(query in str(field).lower() for field in coordinator[1:]):
                self.tree.insert("", "end", values=coordinator[1:])

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.edit_selected_coordinator()

    def edit_selected_coordinator(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un coordinador para editar"
            )
            return

        cedula = self.tree.item(selected[0], "values")[0]

        coordinator_id = self.coordinator_controller.get_id_by_cedula(cedula)

        if not coordinator_id:
            messagebox.showerror("Error", "No se encontró el coordinador por cédula")
            return

        self.show_edit_form(coordinator_id)

    def delete_selected_coordinator(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor, seleccione un coordinador para eliminar"
            )
            return

        cedula = self.tree.item(selected[0], "values")[0]

        # Confirmar eliminación
        confirm = messagebox.askyesno(
            "Confirmar", "¿Está seguro de eliminar este coordinador?"
        )

        if not confirm:
            return

        coordinator_id = self.coordinator_controller.get_id_by_cedula(cedula)

        if not coordinator_id:
            messagebox.showerror("Error", "No se encontró el coordinador por cédula")
            return

        # Eliminar profesor
        try:
            self.coordinator_controller.delete(coordinator_id)
            messagebox.showinfo("Éxito", "Coordinador eliminado correctamente")
            self.load_coordinators()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def show_add_form(self):
        """Muestra el formulario para agregar un nuevo coordinador."""
        form = tk.Toplevel(self.parent)
        form.title("Agregar Coordinador")
        form.geometry("540x270")
        form.transient(self.parent)
        form.grab_set()

        # Campos
        labels = [
            "Cédula",
            "Nombre",
            "Apellido",
            "Carrera",
            "Fecha de Ingreso (YYYY-MM-DD)",
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
                label == "Fecha de Ingreso (YYYY-MM-DD)"
                or label == "Fecha Ingreso (YYYY-MM-DD)"
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
            fecha_ingreso = entries[4].get()

            # Validar campos vacíos
            if (
                not cedula
                or not nombre
                or not apellido
                or not carrera
                or not fecha_ingreso
            ):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            # Validar fecha
            try:
                datetime.strptime(fecha_ingreso, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha inválido. Use YYYY-MM-DD"
                )
                return

            try:
                self.coordinator_controller.create(
                    cedula,
                    nombre,
                    apellido,
                    carrera,
                    fecha_ingreso,
                )
                messagebox.showinfo("Éxito", "Coordinador creado correctamente")
                form.destroy()
                self.load_coordinators()
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

    def show_edit_form(self, coordinator_id):
        """Muestra el formulario para editar un coordinador existente."""
        # Buscar datos actuales
        coordinators = self.coordinator_controller.get_all()
        data = None
        for c in coordinators:
            if str(c[0]) == str(coordinator_id):
                data = c
                break
        if not data:
            messagebox.showerror("Error", "Coordinador no encontrado")
            return

        form = tk.Toplevel(self.parent)
        form.title("Editar Coordinador")
        form.geometry("540x270")
        form.transient(self.parent)
        form.grab_set()

        labels = [
            "Cédula",
            "Nombre",
            "Apellido",
            "Carrera",
            "Fecha Ingreso (YYYY-MM-DD)",
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
                label == "Fecha de Ingreso (YYYY-MM-DD)"
                or label == "Fecha Ingreso (YYYY-MM-DD)"
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
            fecha_ingreso = entries[4].get()

            # Validar campos vacíos
            if (
                not cedula
                or not nombre
                or not apellido
                or not carrera
                or not fecha_ingreso
            ):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            # Validar fecha
            try:
                datetime.strptime(fecha_ingreso, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha inválido. Use YYYY-MM-DD"
                )
                return

            try:
                self.coordinator_controller.update(
                    coordinator_id,
                    cedula,
                    nombre,
                    apellido,
                    carrera,
                    fecha_ingreso,
                )
                messagebox.showinfo("Éxito", "Coordinador actualizado correctamente")
                form.destroy()
                self.load_coordinators()
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
 
        
    
    def cerrar_periodo_academico(self):
            """
        Copia la información de inscripciones y notas finales a materias_cursadas,
        luego elimina todas las secciones, inscripciones y calificaciones.
        """
            periodo_actual = get_periodo_activo()
            if not periodo_actual:
                messagebox.showerror("Error", "No se pudo determinar el período activo.")
                return
    
            confirm = messagebox.askyesno(
                "Confirmar",
                f"¿Está seguro de cerrar el período académico {periodo_actual}? Esto archivará las notas y eliminará todas las secciones activas de este período.",
            )
            if not confirm:
                return
    
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # Solo las secciones activas del periodo actual
                    cursor.execute("SELECT id_seccion, id_materia, periodo FROM secciones WHERE estado = 'activa' AND periodo = ?", (periodo_actual,))
                    secciones = cursor.fetchall()
    
                    for id_seccion, id_materia, periodo in secciones:
                        # Inscripciones de la sección
                        cursor.execute("SELECT id_estudiante, id_inscripcion FROM inscripciones WHERE id_seccion = ?", (id_seccion,))
                        inscripciones = cursor.fetchall()
                        for id_estudiante, id_inscripcion in inscripciones:
                            # Nota final
                            cursor.execute(
                                "SELECT valor_nota FROM calificaciones WHERE id_inscripcion = ? AND tipo_evaluacion = 'nota_def' ORDER BY id_calificacion DESC LIMIT 1",
                                (id_inscripcion,),
                            )
                            nota_row = cursor.fetchone()
                            nota_final = nota_row[0] if nota_row else None
    
                            # Estado académico
                            if nota_final is None:
                                estado = "REPROBÓ"
                            elif nota_final >= 10:
                                estado = "APROBÓ"
                            else:
                                estado = "REPROBÓ"
    
                            # Insertar en materias_cursadas
                            cursor.execute(
                                """
                                INSERT INTO materias_cursadas (id_estudiante, id_materia, periodo, nota_final, estado, fecha_cursada)
                                VALUES (?, ?, ?, ?, ?, DATE('now'))
                                """,
                                (id_estudiante, id_materia, periodo, nota_final, estado),
                            )
    
                    # Eliminar solo datos del periodo actual
                    cursor.execute("DELETE FROM calificaciones WHERE id_inscripcion IN (SELECT id_inscripcion FROM inscripciones WHERE id_seccion IN (SELECT id_seccion FROM secciones WHERE periodo = ?))", (periodo_actual,))
                    cursor.execute("DELETE FROM inscripciones WHERE id_seccion IN (SELECT id_seccion FROM secciones WHERE periodo = ?)", (periodo_actual,))
                    cursor.execute("DELETE FROM secciones WHERE periodo = ?", (periodo_actual,))
                    conn.commit()
    
                # Avanzar al siguiente periodo
                anio, lapso = periodo_actual.split("-")
                if lapso == "1":
                    siguiente = f"{anio}-2"
                else:
                    siguiente = f"{int(anio)+1}-1"
    
                # Si el siguiente periodo no existe, crearlo
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM periodos_academicos WHERE periodo = ?", (siguiente,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO periodos_academicos (periodo, es_activo) VALUES (?, 0)", (siguiente,))
                        conn.commit()
    
                set_periodo_activo(siguiente)
    
                messagebox.showinfo("Éxito", f"Período {periodo_actual} cerrado. Ahora el período activo es {siguiente}.")
                self.load_coordinators()
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")