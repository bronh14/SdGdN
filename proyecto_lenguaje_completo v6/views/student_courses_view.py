import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from controllers.enrollment_controller import EnrollmentController
from controllers.student_controller import StudentController
from models.student import Student
from config.database import get_db_connection, execute_with_retry
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    Table,
    TableStyle,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import uuid
from reportlab.pdfgen import canvas
from pdf.reportesPDF import generar_comprobante_inscripcion_pdf


class StudentCoursesView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.enrollment_controller = EnrollmentController()
        self.student_controller = StudentController()
        self.build()

    def build(self):
        # Limpiar contenido
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Obtener información del estudiante
        estudiante = Student.get_by_user_id(self.user.id)
        if not estudiante:
            messagebox.showerror("Error", "No se encontró información del estudiante.")
            return

        self.estudiante = estudiante  # Guardar referencia para usar en otras funciones

        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame, text="Mis Materias", font=("Arial", 16, "bold"), bg="white"
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Información del estudiante
        info_frame = tk.Frame(self.parent, bg="#f5f5f5")
        info_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            info_frame,
            text=f"Estudiante: {self.user.nombre} {self.user.apellido}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5",
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text=f"Carrera: {estudiante.carrera}",
            font=("Arial", 11),
            bg="#f5f5f5",
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text=f"Semestre Actual: {estudiante.semestre}",
            font=("Arial", 11),
            bg="#f5f5f5",
        ).pack(anchor="w")

        # Botones de acción en la parte superior
        action_frame = tk.Frame(self.parent, bg="#f5f5f5")
        action_frame.pack(fill="x", padx=20, pady=5)

        # Botón para generar comprobante de inscripción
        generar_btn = tk.Button(
            action_frame,
            text="Generar Comprobante de Inscripción",
            font=("Arial", 10, "bold"),
            command=self.generar_comprobante_inscripcion,
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=10,
            pady=5,
        )
        generar_btn.pack(side="left", padx=(0, 10))

        # Botón de actualizar
        refresh_btn = tk.Button(
            action_frame,
            text="Actualizar",
            font=("Arial", 10, "bold"),
            command=lambda: self.load_student_courses(estudiante.id),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=10,
            pady=5,
        )
        refresh_btn.pack(side="left")

        # Contenido principal
        main_frame = tk.Frame(self.parent, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla de materias inscritas
        tk.Label(
            main_frame,
            text="MATERIAS INSCRITAS:",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5",
        ).pack(anchor="w", pady=(0, 10))

        # Frame para la tabla
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        # Crear Treeview
        columns = (
            "codigo",
            "materia",
            "creditos",
            "seccion",
            "profesor",
            "aula",
            "fecha_inscripcion",
            "calificacion",
            "estado",
        )
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=12
        )

        # Configurar encabezados
        headers = {
            "codigo": ("Código", 80),
            "materia": ("Materia", 250),
            "creditos": ("UC", 50),
            "seccion": ("Sección", 70),
            "profesor": ("Profesor", 180),
            "aula": ("Aula", 70),
            "fecha_inscripcion": ("Fecha de Inscripción", 150),
            "calificacion": ("Calificación", 100),
            "estado": ("Estado", 100),
        }

        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Empaquetar tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Frame para estadísticas
        stats_frame = tk.Frame(main_frame, bg="#f5f5f5")
        stats_frame.pack(fill="x", pady=(20, 0))

        self.stats_label = tk.Label(
            stats_frame, text="", font=("Arial", 11, "bold"), bg="#f5f5f5", fg="#2980b9"
        )
        self.stats_label.pack(anchor="w")

        # Cargar datos
        self.load_student_courses(estudiante.id)

    def load_student_courses(self, student_id):
        """Carga los cursos del estudiante"""

        def _load_courses():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        m.codigo,
                        m.nombre,
                        m.creditos,
                        s.numero_seccion,
                        s.periodo,
                        COALESCE(u.nombre || ' ' || u.apellido, 'Por asignar') as profesor,
                        COALESCE(s.aula, 'Por asignar') as aula,
                        i.fecha_inscripcion,
                        -- Calificación definitiva (nota final)
                        (
                            SELECT valor_nota 
                            FROM calificaciones c 
                            WHERE c.id_inscripcion = i.id_inscripcion AND c.tipo_evaluacion = 'nota_def'
                            ORDER BY c.id_calificacion DESC LIMIT 1
                        ) as calificacion,
                        -- Estado académico calculado dinámicamente
                        (
                            CASE
                                WHEN (
                                    SELECT valor_nota 
                                    FROM calificaciones c 
                                    WHERE c.id_inscripcion = i.id_inscripcion AND c.tipo_evaluacion = 'nota_def'
                                    ORDER BY c.id_calificacion DESC LIMIT 1
                                ) IS NULL THEN '-'
                                WHEN (
                                    SELECT valor_nota 
                                    FROM calificaciones c 
                                    WHERE c.id_inscripcion = i.id_inscripcion AND c.tipo_evaluacion = 'nota_def'
                                    ORDER BY c.id_calificacion DESC LIMIT 1
                                ) >= 10 THEN 'APROBÓ'
                                ELSE 'REPROBÓ'
                            END
                        ) as estado_academico
                    FROM inscripciones i
                    JOIN secciones s ON i.id_seccion = s.id_seccion
                    JOIN materias m ON s.id_materia = m.id_materia
                    LEFT JOIN profesores p ON s.id_profesor = p.id_profesor
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE i.id_estudiante = ?
                    ORDER BY s.periodo DESC, m.codigo
                """,
                    (student_id,),
                )
                return cursor.fetchall()

        try:
            # Cargar cursos
            cursos = execute_with_retry(_load_courses)

            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insertar cursos directamente en la tabla sin agrupar por período
            for curso in cursos:
                (
                    codigo,
                    nombre,
                    creditos,
                    numero_seccion,
                    periodo,
                    profesor,
                    aula,
                    fecha,
                    calificacion,
                    estado_academico,
                ) = curso

                # Formatear calificación
                calificacion_str = (
                    f"{calificacion:.2f}" if calificacion is not None else "-"
                )

                # Estado académico
                estado_str = estado_academico if estado_academico else "-"

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        codigo,
                        nombre,
                        creditos,
                        f"D{numero_seccion}",
                        profesor,
                        aula,
                        fecha,
                        calificacion_str,
                        estado_str,
                    ),
                )

            # Eliminar la configuración de estilo para los encabezados de período, ya no son necesarios
            # self.tree.tag_configure("periodo", font=("Arial", 10, "bold"), background="#f0f0f0")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar cursos: {str(e)}")

    def _get_materias_para_pdf(self):
        materias = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            materias.append(
                (
                    values[0],  # codigo
                    values[1],  # nombre
                    values[2],  # creditos
                    values[3].replace("D", ""),  # seccion (solo número)
                    values[4],  # profesor
                )
            )
        return materias

    def generar_comprobante_inscripcion(self):
        # Selecciona la ruta donde guardar el PDF
        cedula = self.user.cedula
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"comprobante_inscripcion_{cedula}.pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar comprobante de inscripción",
        )
        if not file_path:
            return

        materias = self._get_materias_para_pdf()
        if not materias:
            messagebox.showwarning(
                "Sin materias", "No hay materias inscritas para generar el comprobante."
            )
            return

        self._crear_pdf_comprobante(file_path, materias)
        messagebox.showinfo("Éxito", "Comprobante generado correctamente.")

    def _crear_pdf_comprobante(self, file_path, materias):
        # Obtener datos del usuario asociado al estudiante
        cedula = self.user.cedula
        nombre = self.user.nombre
        apellido = self.user.apellido
        carrera = self._get_programa_name()
        # Llama a la función del PDF
        generar_comprobante_inscripcion_pdf(
            file_path, materias, cedula, nombre, apellido, carrera
        )
        # Abrir automáticamente el PDF después de generarlo
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showwarning(
                "Aviso",
                f"El comprobante se generó correctamente, pero no se pudo abrir automáticamente:\n{str(e)}",
            )

    def _get_programa_name(self):
        """Obtiene el nombre completo del programa según la carrera"""
        carrera_map = {
            "Ingeniería en Sistemas": "INGENIERÍA EN SISTEMAS - DIURNO",
            "Ingeniería Mecánica": "INGENIERÍA MECÁNICA - DIURNO",
            "Ingeniería Naval": "INGENIERÍA NAVAL - DIURNO",
            "Enfermería": "T.S.U EN ENFERMERÍA - DIURNO",
        }
        return carrera_map.get(
            self.estudiante.carrera, f"{self.estudiante.carrera.upper()} - DIURNO"
        )
