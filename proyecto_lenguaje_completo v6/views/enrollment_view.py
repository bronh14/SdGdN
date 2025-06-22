import tkinter as tk
import os
from tkinter import filedialog
from config.database import (
    get_db_connection,
    execute_with_retry,
    get_periodo_activo,
    get_periodos_disponibles,
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import ttk, messagebox
from models.course import Course
from controllers.enrollment_controller import EnrollmentController
from controllers.student_controller import StudentController


class EnrollmentView:
    def __init__(self, parent, estudiante):
        self.parent = parent
        self.estudiante = estudiante
        self.controller = EnrollmentController()
        self.student_controller = StudentController()
        self.materias_seleccionadas = []
        self.uc_inscritas = 0
        self.secciones_seleccionadas = (
            {}
        )  # Diccionario para guardar sección por materia
        # Verificar si el estudiante ya se inscribió ANTES de construir la interfaz
        self.ya_inscrito = self.verificar_inscripcion_existente()
        # Ahora construimos la interfaz
        self.build()

    def verificar_inscripcion_existente(self):
        """Verifica si el estudiante ya tiene inscripciones activas para este período"""

        def _verificar():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM inscripciones i
                    JOIN secciones s ON i.id_seccion = s.id_seccion
                    WHERE i.id_estudiante = ? AND i.estado = 'activo'
                    """,
                    (self.estudiante.id,),
                )
                return cursor.fetchone()[0] > 0

        try:
            return execute_with_retry(_verificar)
        except Exception:
            return False

    def build(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        carrera = self.estudiante.carrera
        tk.Label(
            self.parent, text=f"Inscripción de materias", font=("Arial", 16, "bold")
        ).pack(pady=5)
        tk.Label(self.parent, text=f"{carrera}", font=("Arial", 12)).pack(pady=2)

        # Verificar si ya se inscribió
        if self.ya_inscrito:
            self.mostrar_vista_inscrito()
            return

        # Frame para selectores
        selectores_frame = tk.Frame(self.parent)
        selectores_frame.pack(pady=5)

        # Selector de semestre
        tk.Label(selectores_frame, text="Semestre:", font=("Arial", 12)).pack(
            side="left", padx=5
        )
        if carrera == "Enfermería":
            semestres = list(range(1, 6))
        else:
            semestres = list(range(1, 10))
        self.semestre_var = tk.IntVar(value=semestres[0])
        self.semestre_cb = ttk.Combobox(
            selectores_frame,
            textvariable=self.semestre_var,
            values=semestres,
            state="readonly",
            width=5,
        )
        self.semestre_cb.pack(side="left", padx=5)
        self.semestre_cb.bind(
            "<<ComboboxSelected>>", lambda e: self.actualizar_tabla_materias()
        )

        # Selector de período
        tk.Label(selectores_frame, text="Período:", font=("Arial", 12)).pack(
            side="left", padx=5
        )
        self.periodo_var = tk.StringVar()
        self.periodo_cb = ttk.Combobox(
            selectores_frame, textvariable=self.periodo_var, state="readonly", width=10
        )
        self.periodo_cb.pack(side="left", padx=5)

        # Cargar períodos disponibles
        periodos = get_periodos_disponibles()
        self.periodo_cb["values"] = [p[0] for p in periodos]

        # Establecer el período activo por defecto
        periodo_activo = get_periodo_activo()
        if periodo_activo:
            self.periodo_var.set(periodo_activo)
        elif periodos:
            self.periodo_var.set(periodos[0][0])

        # NUEVO: Label para mostrar la suma total de UC del semestre
        self.uc_total_semestre_label = tk.Label(
            selectores_frame,
            text="Total UC semestre: 0",
            font=("Arial", 10, "bold"),
            fg="#2980b9",
        )
        self.uc_total_semestre_label.pack(side="left", padx=15)

        columns = ("id", "codigo", "nombre", "uc", "requisito", "estado")
        tree_frame = tk.Frame(self.parent)
        tree_frame.pack(pady=10)

        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=10
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Asignatura")
        self.tree.heading("uc", text="UC")
        self.tree.heading("requisito", text="Requisito")
        self.tree.heading("estado", text="Estado")
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("codigo", width=100, anchor="center")
        self.tree.column("nombre", width=280, anchor="center")
        self.tree.column("uc", width=40, anchor="center")
        self.tree.column("requisito", width=180, anchor="center")
        self.tree.column("estado", width=60, anchor="center")
        self.tree.pack(side="left", padx=10, pady=5)

        tree_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.pack(side="right", fill="y", pady=5)

        # Leyenda de iconos
        legend_frame = tk.Frame(self.parent)
        legend_frame.pack(pady=2)
        tk.Label(legend_frame, text="✅ Asignatura aprobada   ").pack(side="left")
        tk.Label(legend_frame, text="📝 Inscribir asignatura   ").pack(side="left")
        tk.Label(legend_frame, text="📋 Asignatura inscrita   ").pack(side="left")
        tk.Label(legend_frame, text="🔐 Asignatura prelación   ").pack(side="left")
        tk.Label(legend_frame, text="⚠️ Insuficientes unidades de crédito").pack(
            side="left"
        )

        # Tabla de materias a inscribir
        tk.Label(
            self.parent,
            text="ASIGNATURAS INSCRITAS:",
            font=("Arial", 11, "bold"),
        ).pack(anchor="center", fill="x", pady=5)

        # Frame para la tabla y el scrollbar
        inscribir_frame = tk.Frame(self.parent)
        inscribir_frame.pack(pady=0)

        self.inscribir_tree = ttk.Treeview(
            inscribir_frame,
            columns=(
                "id",
                "codigo",
                "nombre",
                "uc",
                "requisito",
                "seccion",
                "internal_seccion_id",
            ),
            show="headings",
            height=5,
        )
        for col, txt, w in zip(
            (
                "id",
                "codigo",
                "nombre",
                "uc",
                "requisito",
                "seccion",
                "internal_seccion_id",
            ),
            (
                "ID",
                "Código",
                "Asignatura",
                "UC",
                "Requisito",
                "Sección",
                "ID_Seccion_Oculto",
            ),
            (40, 100, 280, 40, 180, 60, 0),
        ):
            self.inscribir_tree.heading(col, text=txt)
            self.inscribir_tree.column(col, width=w)
            self.inscribir_tree.column("id", width=40, anchor="center")
            self.inscribir_tree.column("codigo", width=100, anchor="center")
            self.inscribir_tree.column("nombre", width=280, anchor="center")
            self.inscribir_tree.column("uc", width=40, anchor="center")
            self.inscribir_tree.column("requisito", width=180, anchor="center")
            self.inscribir_tree.column("seccion", width=60, anchor="center")
            self.inscribir_tree.column("internal_seccion_id", width=0, stretch=tk.NO)

        # Scrollbar vertical
        inscribir_scrollbar = ttk.Scrollbar(
            inscribir_frame, orient="vertical", command=self.inscribir_tree.yview
        )
        self.inscribir_tree.configure(yscrollcommand=inscribir_scrollbar.set)
        self.inscribir_tree.pack(side="left", padx=10, pady=5)
        inscribir_scrollbar.pack(side="right", fill="y")

        self.materias_a_inscribir = set()
        self.icon_tooltips = {
            "✅": "Asignatura aprobada",
            "🔐": "Asignatura con prelación",
            "📝": "Inscribir asignatura",
            "📋": "Asignatura ya inscrita",
            "⚠️": "Insuficientes unidades de crédito",
        }

        # Frame para los botones de acción
        botones_frame = tk.Frame(self.parent)
        botones_frame.pack(pady=5)

        # Botón para retirar materia
        retirar_btn = tk.Button(
            botones_frame,
            text="Retirar materia seleccionada",
            font=("Arial", 10, "bold"),
            command=self.retirar_materia,
            bg="#e74c3c",  # Rojo suave
            fg="white",  # Texto blanco
            activebackground="#c0392b",  # Rojo más oscuro al presionar
            activeforeground="white",
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        retirar_btn.pack(side="left", pady=5, padx=5)

        # Botón para inscribir un estudiante
        inscribir_estudiante_btn = tk.Button(
            botones_frame,
            text="Inscribirse",
            font=("Arial", 10, "bold"),
            command=self.inscribir_seleccion,
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            relief="raised",
            bd=2,
            cursor="hand2",
        )
        inscribir_estudiante_btn.pack(side="left", pady=5, padx=5)

        self.uc_label = tk.Label(
            self.parent,
            text=f"UC disponibles: {33 - self.uc_inscritas}",
            font=("Arial", 10, "bold"),
        )
        self.uc_label.pack(pady=2)

        self.actualizar_tabla_materias()
        self.tree.bind("<Motion>", self.on_hover)
        self.tree.bind("<Button-1>", self.on_click)
        self._tooltip = None

    def mostrar_vista_inscrito(self):
        """Muestra una vista de solo lectura cuando el estudiante ya se inscribió"""
        # Mensaje principal
        mensaje_frame = tk.Frame(self.parent, bg="#e8f5e8", relief="solid", bd=2)
        mensaje_frame.pack(fill="x", padx=20, pady=20)

        tk.Label(
            mensaje_frame,
            text="✅ INSCRIPCIÓN COMPLETADA",
            font=("Arial", 16, "bold"),
            fg="#27ae60",
            bg="#e8f5e8",
        ).pack(pady=10)

        tk.Label(
            mensaje_frame,
            text="Ya te has inscrito para este período académico.",
            font=("Arial", 12),
            fg="#2c3e50",
            bg="#e8f5e8",
        ).pack(pady=(0, 5))

        tk.Label(
            mensaje_frame,
            text="No puedes realizar más cambios en tu inscripción.",
            font=("Arial", 11),
            fg="#7f8c8d",
            bg="#e8f5e8",
        ).pack(pady=(0, 10))

        # Mostrar materias inscritas
        tk.Label(
            self.parent,
            text="MATERIAS INSCRITAS:",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Tabla de materias inscritas (solo lectura)
        table_frame = tk.Frame(self.parent)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("codigo", "nombre", "creditos", "seccion", "profesor")
        self.tree_readonly = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=10
        )

        headers = {
            "codigo": ("Código", 100),
            "nombre": ("Asignatura", 300),
            "creditos": ("UC", 50),
            "seccion": ("Sección", 80),
            "profesor": ("Profesor", 200),
        }

        for col, (text, width) in headers.items():
            self.tree_readonly.heading(col, text=text)
            self.tree_readonly.column(col, width=width, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree_readonly.yview
        )
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.tree_readonly.xview
        )
        self.tree_readonly.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        self.tree_readonly.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Cargar y mostrar materias inscritas
        self.cargar_materias_inscritas()

        # Frame para estadísticas
        stats_frame = tk.Frame(self.parent)
        stats_frame.pack(fill="x", padx=20, pady=10)

        self.stats_readonly_label = tk.Label(
            stats_frame, text="", font=("Arial", 11, "bold"), fg="#2980b9"
        )
        self.stats_readonly_label.pack(anchor="w")

        # Botón para ir a "Mis Materias"
        action_frame = tk.Frame(self.parent)
        action_frame.pack(pady=20)

        ver_materias_btn = tk.Button(
            action_frame,
            text="📚 Ver Mis Materias Completo",
            font=("Arial", 11, "bold"),
            command=self.ir_a_mis_materias,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=20,
            pady=8,
        )
        ver_materias_btn.pack()

    def inscribir_seleccion(self):
        """Inscribe las materias seleccionadas en la base de datos"""
        if not self.materias_a_inscribir:
            messagebox.showinfo(
                "Inscripción", "No hay materias seleccionadas para inscribir."
            )
            return

        periodo = self.periodo_var.get()
        if not periodo:
            messagebox.showerror("Error", "Debe seleccionar un período académico.")
            return

        def _inscribir():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                materias_inscritas = []

                # Procesar cada materia a inscribir
                for item in self.inscribir_tree.get_children():
                    values = self.inscribir_tree.item(item, "values")
                    codigo_materia = values[1]
                    # Obtener directamente el id_seccion de la columna oculta
                    id_seccion = values[6]

                    # Obtener ID de la materia
                    cursor.execute(
                        "SELECT id_materia FROM materias WHERE codigo = ?",
                        (codigo_materia,),
                    )
                    materia_row = cursor.fetchone()
                    if not materia_row:
                        continue

                    id_materia = materia_row[0]

                    # Verificar si ya está inscrito
                    cursor.execute(
                        """
                        SELECT id_inscripcion FROM inscripciones 
                        WHERE id_estudiante = ? AND id_seccion = ?
                    """,
                        (self.estudiante.id, id_seccion),
                    )

                    if not cursor.fetchone():
                        # Crear inscripción
                        cursor.execute(
                            """
                            INSERT INTO inscripciones (id_estudiante, id_seccion, fecha_inscripcion)
                            VALUES (?, ?, date('now'))
                        """,
                            (self.estudiante.id, id_seccion),
                        )

                        materias_inscritas.append(codigo_materia)

                # Actualizar semestre del estudiante
                nuevo_semestre = self.semestre_var.get()
                cursor.execute(
                    """
                    UPDATE estudiantes 
                    SET semestre = ? 
                    WHERE id_estudiante = ?
                """,
                    (nuevo_semestre, self.estudiante.id),
                )

                conn.commit()
                return materias_inscritas, nuevo_semestre

        try:
            result = execute_with_retry(_inscribir)
            if result is None:
                return

            materias_inscritas, nuevo_semestre = result

            # Actualizar el objeto estudiante
            self.estudiante.semestre = nuevo_semestre

            # Reload inscribed courses from the database
            self.cargar_materias_inscritas_a_inscribir_tree()
            self.actualizar_tabla_materias()
            self.uc_label.config(text=f"UC disponibles: {33 - self.uc_inscritas}")

            messagebox.showinfo(
                "Inscripción Exitosa",
                f"Se inscribieron {len(materias_inscritas)} materias correctamente.\n"
                f"Semestre actualizado a: {nuevo_semestre}",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al inscribir materias: {str(e)}")

    def cargar_materias_inscritas_a_inscribir_tree(self):
        def _cargar():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        m.codigo,
                        m.nombre,
                        m.creditos,
                        COALESCE(s.numero_seccion, 1) as numero_seccion,
                        COALESCE(u.nombre || ' ' || u.apellido, 'No asignado') as profesor,
                        m.requisitos
                    FROM inscripciones i
                    JOIN secciones s ON i.id_seccion = s.id_seccion
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN profesores p ON s.id_profesor = p.id_profesor
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE i.id_estudiante = ? AND i.estado = 'activo'
                    ORDER BY m.codigo
                    """,
                    (self.estudiante.id,),
                )
                return cursor.fetchall()

        try:
            # Clear the inscribir_tree
            for item in self.inscribir_tree.get_children():
                self.inscribir_tree.delete(item)

            materias = execute_with_retry(_cargar)
            self.uc_inscritas = 0
            self.materias_a_inscribir.clear()
            self.secciones_seleccionadas.clear()

            for idx, materia in enumerate(materias, start=1):
                codigo, nombre, creditos, numero_seccion, profesor, requisitos = materia
                self.uc_inscritas += int(creditos)
                nombre_seccion = f"D{numero_seccion}"
                self.materias_a_inscribir.add(codigo)
                self.secciones_seleccionadas[codigo] = nombre_seccion
                self.inscribir_tree.insert(
                    "",
                    tk.END,
                    values=(
                        idx,
                        codigo,
                        nombre,
                        creditos,
                        requisitos if requisitos else "-",
                        nombre_seccion,
                        numero_seccion,
                    ),
                )

        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al cargar materias inscritas: {str(e)}"
            )

    def actualizar_tabla_materias(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        carrera = self.estudiante.carrera
        semestre = self.semestre_var.get()

        materias = [
            m
            for m in Course.get_all()
            if m.carrera.strip().lower() == carrera.strip().lower()
            and int(m.semestre) == int(semestre)
        ]

        # NUEVO: Calcular la suma total de UC del semestre
        total_uc_semestre = sum(int(m.creditos) for m in materias)
        self.uc_total_semestre_label.config(
            text=f"Total UC semestre: {total_uc_semestre}"
        )

        self.cantidad_materias_semestre = len(materias)

        # --- Cambios aquí: obtener códigos de materias aprobadas ---
        materias_cursadas = self.controller.get_materias_cursadas(self.estudiante.id)
        materias_aprobadas_ids = {m["id_materia"] for m in materias_cursadas if m["estado"] == "APROBÓ"}
        # Obtener los códigos de las materias aprobadas
        materias_aprobadas_codigos = set()
        for m in Course.get_all():
            if m.id in materias_aprobadas_ids:
                materias_aprobadas_codigos.add(m.codigo)

        materias_inscritas = self.controller.get_materias_inscritas(self.estudiante.id)

        self.materia_info = {}

        uc_disponibles = 33 - self.uc_inscritas

        for idx, materia in enumerate(materias, start=1):
            if materia.codigo in materias_aprobadas_codigos:
                estado = "✅"
            elif materia.codigo in self.materias_a_inscribir:
                estado = "📋"
            elif materia.id in materias_inscritas:
                estado = "📋"
            elif materia.requisitos:
                req_codigos = [
                    r.strip() for r in materia.requisitos.split("/") if r.strip()
                ]
                req_ids = []
                corequisito_ok = True
                for req_codigo in req_codigos:
                    if req_codigo.startswith("CO-"):
                        co_codigo = req_codigo[3:]
                        # Puede inscribir si el corequisito está aprobado o lo está inscribiendo ahora
                        co_aprobada = False
                        if (
                            co_codigo in materias_aprobadas_codigos
                            or co_codigo in self.materias_a_inscribir
                        ):
                            co_aprobada = True
                        if not co_aprobada:
                            corequisito_ok = False
                    else:
                        # Requisito normal: debe estar aprobado
                        if req_codigo not in materias_aprobadas_codigos:
                            req_ids.append(req_codigo)
                # Si todos los requisitos normales están aprobados y los corequisitos están ok
                if (
                    not req_ids
                    and corequisito_ok
                ):
                    if int(materia.creditos) > uc_disponibles:
                        estado = "⚠️"
                    else:
                        estado = "📝"
                else:
                    estado = "🔐"
            else:
                if int(materia.creditos) > uc_disponibles:
                    estado = "⚠️"
                else:
                    estado = "📝"

            item_id = self.tree.insert(
                "",
                tk.END,
                values=(
                    idx,
                    materia.codigo,
                    materia.nombre,
                    materia.creditos,
                    materia.requisitos if materia.requisitos else "-",
                    estado,
                ),
            )
            self.materia_info[item_id] = {
                "id_materia": materia.id,
                "codigo": materia.codigo,
                "nombre": materia.nombre,
                "uc": materia.creditos,
                "requisito": materia.requisitos if materia.requisitos else "-",
                "estado": estado,
            }

    def on_hover(self, event):
        region = self.tree.identify("region", event.x, event.y)
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if region == "cell" and col == "#6" and row_id in self.materia_info:
            estado = self.materia_info[row_id]["estado"]
            texto = self.icon_tooltips.get(estado, "")
            if texto:
                # Obtén la posición de la celda
                bbox = self.tree.bbox(row_id, col)
                if bbox:
                    x, y, width, height = bbox
                    x += self.tree.winfo_rootx()
                    y += self.tree.winfo_rooty()
                    if not self._tooltip:
                        self._tooltip = Tooltip(self.tree, texto)
                    self._tooltip.show_tip_at(x, y + height)
                    return
        if self._tooltip:
            self._tooltip.hide_tip()
            self._tooltip = None

    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)
            if col == "#6" and row_id in self.materia_info:  # columna de estado
                info = self.materia_info[row_id]
                if info["estado"] == "✅":
                    messagebox.showinfo(
                        "No permitido",
                        "No puedes inscribir una materia que ya aprobaste.",
                    )
                    return
                if info["estado"] == "📝":
                    nueva_uc = int(info["uc"])
                    if self.uc_inscritas + nueva_uc > 33:
                        messagebox.showwarning(
                            "Límite de UC",
                            "No puedes inscribir más de 33 unidades de crédito.",
                        )
                        return

                    # Crear diálogo de confirmación con selector de sección
                    dialog = tk.Toplevel(self.parent)
                    dialog.title("Confirmar inscripción")
                    dialog.resizable(False, False)
                    dialog.transient(self.parent)

                    # Centrar el diálogo
                    parent_x = self.parent.winfo_rootx()
                    parent_y = self.parent.winfo_rooty()
                    parent_width = self.parent.winfo_width()
                    parent_height = self.parent.winfo_height()
                    dialog_width = 350
                    dialog_height = 150
                    x = parent_x + (parent_width // 2) - (dialog_width // 2)
                    y = parent_y + (parent_height // 2) - (dialog_height // 2)
                    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

                    # Contenido del diálogo
                    main_frame = tk.Frame(dialog, padx=10, pady=10)
                    main_frame.pack(expand=True, fill="both")

                    tk.Label(
                        main_frame,
                        text=f"¿Deseas inscribir la materia:",
                        font=("Arial", 10),
                    ).pack(anchor="w")

                    tk.Label(
                        main_frame,
                        text=f"'{info['nombre']}'?",
                        font=("Arial", 10, "bold"),
                    ).pack(anchor="w", pady=(0, 10))

                    # Frame para la selección de sección
                    section_frame = tk.Frame(main_frame)
                    section_frame.pack(fill="x", pady=5)
                    tk.Label(section_frame, text="Sección:", font=("Arial", 10)).pack(
                        side="left", padx=5
                    )
                    section_var = tk.StringVar()
                    section_combobox = ttk.Combobox(
                        section_frame,
                        textvariable=section_var,
                        state="readonly",
                        width=5,
                        font=("Arial", 10),
                    )
                    section_combobox.pack(side="left")

                    # Almacenar el mapeo de numero_seccion a id_seccion
                    self.secciones_map = {}

                    # Cargar secciones disponibles para la materia y el período activo
                    materia_id_seleccionada = info["id_materia"]
                    periodo_activo = self.periodo_var.get()

                    secciones_disponibles = (
                        self.controller.get_sections_by_materia_and_periodo(
                            materia_id_seleccionada, periodo_activo
                        )
                    )

                    # Filtrar secciones para mostrar solo 1, 2, 3
                    secciones_a_mostrar = []
                    for s_id, s_num in secciones_disponibles:
                        if str(s_num).strip() in ["1", "2", "3"]:
                            self.secciones_map[str(s_num).strip()] = s_id
                            secciones_a_mostrar.append(str(s_num).strip())

                    if secciones_a_mostrar:
                        section_combobox["values"] = secciones_a_mostrar
                        section_var.set(secciones_a_mostrar[0])
                    else:
                        section_combobox["values"] = []
                        section_var.set("No hay secciones")
                        messagebox.showwarning(
                            "Sin secciones",
                            f"No hay secciones 1, 2 o 3 disponibles para {info['nombre']} en el período {periodo_activo}.",
                        )
                        dialog.destroy()
                        return

                    # Frame para los botones
                    button_frame = tk.Frame(main_frame)
                    button_frame.pack(fill="x", pady=(10, 0))

                    def confirm():
                        section_num = section_var.get().strip()
                        if section_num == "No hay secciones":
                            messagebox.showerror(
                                "Error", "No se puede inscribir sin una sección válida."
                            )
                            return

                        seccion_id = self.secciones_map.get(section_num)
                        if seccion_id is None:
                            messagebox.showerror(
                                "Error", "Sección no válida seleccionada."
                            )
                            return

                        dialog.destroy()
                        if info["codigo"] not in self.materias_a_inscribir:
                            try:
                                self.controller.create(
                                    self.estudiante.id, int(seccion_id)
                                )
                            except Exception as e:
                                messagebox.showerror(
                                    "Error al inscribir materias", str(e)
                                )
                                return

                            idx = len(self.inscribir_tree.get_children()) + 1
                            self.inscribir_tree.insert(
                                "",
                                tk.END,
                                values=(
                                    idx,
                                    info["codigo"],
                                    info["nombre"],
                                    info["uc"],
                                    info["requisito"],
                                    f"D{section_num}",
                                    seccion_id,
                                ),
                            )
                            self.materias_a_inscribir.add(info["codigo"])
                            self.secciones_seleccionadas[info["codigo"]] = section_num
                            self.uc_inscritas += nueva_uc
                            self.materia_info[row_id]["estado"] = "📋"
                            self.actualizar_tabla_materias()
                            self.uc_label.config(
                                text=f"UC disponibles: {33 - self.uc_inscritas}"
                            )

                    inner_button_frame = tk.Frame(button_frame)
                    inner_button_frame.pack(expand=True)

                    yes_btn = tk.Button(
                        inner_button_frame,
                        text="Sí",
                        command=confirm,
                        width=8,
                        font=("Arial", 10),
                        bg="#4CAF50",
                        fg="white",
                        activebackground="#45a049",
                        relief="raised",
                        bd=2,
                    )
                    yes_btn.pack(side="left", padx=10)

                    no_btn = tk.Button(
                        inner_button_frame,
                        text="No",
                        command=dialog.destroy,
                        width=8,
                        font=("Arial", 10),
                        bg="#f44336",
                        fg="white",
                        activebackground="#d32f2f",
                        relief="raised",
                        bd=2,
                    )
                    no_btn.pack(side="left", padx=10)

                    dialog.grab_set()
                    dialog.wait_window()
                else:
                    messagebox.showinfo(
                        "Información",
                        self.icon_tooltips.get(info["estado"], "No disponible"),
                    )

    def retirar_materia(self):
        selected = self.inscribir_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Retirar materia", "Selecciona una materia para retirar."
            )
            return
        for item in selected:
            values = self.inscribir_tree.item(item, "values")
            codigo = values[1]
            uc = int(values[3])
            # Elimina de la tabla visual
            self.inscribir_tree.delete(item)
            # Elimina del set de materias a inscribir
            if codigo in self.materias_a_inscribir:
                self.materias_a_inscribir.remove(codigo)
                if codigo in self.secciones_seleccionadas:
                    del self.secciones_seleccionadas[codigo]
                self.uc_inscritas -= uc
                if self.uc_inscritas < 0:
                    self.uc_inscritas = 0
            # Reasigna los IDs para mantenerlos consecutivos
            for idx, iid in enumerate(self.inscribir_tree.get_children(), start=1):
                vals = list(self.inscribir_tree.item(iid, "values"))
                vals[0] = idx
                self.inscribir_tree.item(iid, values=vals)
            # Actualiza el contador y la tabla principal
            self.uc_label.config(text=f"UC disponibles: {33 - self.uc_inscritas}")
            self.actualizar_tabla_materias()

    def cargar_materias_inscritas(self):
        """Carga las materias inscritas del estudiante"""

        def _cargar():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        m.codigo,
                        m.nombre,
                        m.creditos,
                        COALESCE(s.numero_seccion, 1) as numero_seccion,
                        COALESCE(u.nombre || ' ' || u.apellido, 'No asignado') as profesor
                    FROM inscripciones i
                    JOIN secciones s ON i.id_seccion = s.id_seccion
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN profesores p ON s.id_profesor = p.id_profesor
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE i.id_estudiante = ? AND i.estado = 'activo'
                    ORDER BY m.codigo
                """,
                    (self.estudiante.id,),
                )
                return cursor.fetchall()

        try:
            materias = execute_with_retry(_cargar)

            total_creditos = 0
            for materia in materias:
                codigo, nombre, creditos, numero_seccion, profesor = materia
                total_creditos += int(creditos)

                # Convertir numero_seccion a formato D1, D2, D3, etc.
                nombre_seccion = f"D{numero_seccion}"

                self.tree_readonly.insert(
                    "",
                    "end",
                    values=(codigo, nombre, creditos, nombre_seccion, profesor),
                )

            # Actualizar estadísticas
            if hasattr(self, "stats_readonly_label"):
                self.stats_readonly_label.config(
                    text=f"Total de materias: {len(materias)} | Total de créditos: {total_creditos} UC"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar materias: {str(e)}")

    def ir_a_mis_materias(self):
        """Navega a la vista de Mis Materias"""
        # Aquí puedes implementar la navegación a la vista de materias
        # Por ejemplo, si tienes un sistema de navegación:
        messagebox.showinfo(
            "Información",
            "Dirígete a la sección 'Mis Materias' para ver el detalle completo de tu inscripción.",
        )


# Modifica tu clase Tooltip para aceptar coordenadas:
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None

    def show_tip_at(self, x, y):
        if self.tipwindow or not self.text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", "10", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
