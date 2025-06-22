import tkinter as tk
import matplotlib.ticker as mticker
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pdf import reportesPDF
from config import database
from models.student import Student
import os
import traceback
import sqlite3
from config.database import get_db_connection, execute_with_retry
from models.coordinator import Coordinator
from datetime import datetime


class ReportView:
    def __init__(self, parent, app_controller, user):
        self.parent = parent
        self.app_controller = app_controller
        self.user = user

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Reportes y Estadísticas",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Contenido
        content_container = tk.Frame(self.parent, bg="#f5f5f5")
        content_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Selector de reportes
        selector_frame = tk.Frame(content_container, bg="white", padx=15, pady=15)
        selector_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            selector_frame,
            text="Seleccione un reporte:",
            font=("Arial", 12, "bold"),
            bg="white",
        ).pack(side="left", padx=(0, 10))

        if hasattr(self.user, "rol"):
            rol = self.user.rol.lower()
            if rol == "alumno":
                report_types = [
                    "Record Academico",
                    "Constancia de Estudio",
                ]
            elif rol in ("administrador"):
                report_types = [
                    "Estudiantes por Carrera",
                    "Profesores por Carrera",
                    "Materias por Carrera",
                ]
            elif rol in ("coordinacion"):
                report_types = [
                    "Estudiantes por semestre",
                    "Profesores por materias",
                ]
            else:
                report_types = []
        else:
            report_types = []

        self.report_combo = ttk.Combobox(
            selector_frame,
            font=("Arial", 12),
            width=30,
            values=report_types,
            state="readonly",
        )
        self.report_combo.pack(side="left", padx=10)
        self.report_combo.current(0)

        generate_btn = tk.Button(
            selector_frame,
            text="Generar Reporte",
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=15,
            pady=5,
            command=self.generate_report,
        )
        generate_btn.pack(side="left", padx=10)

        # Área de reporte
        self.report_frame = tk.Frame(content_container, bg="white", padx=15, pady=15)
        self.report_frame.pack(fill="both", expand=True)

        # # Generar reporte inicial
        # self.generate_report()

    def generate_report(self):
        # Limpiar área de reporte
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        self.report_frame.pack_forget()
        self.report_frame.pack(fill="both", expand=True)

        report_type = self.report_combo.get()

        if report_type == "Estudiantes por Carrera":
            self.generate_students_by_career_report()
        elif report_type == "Profesores por Carrera":
            self.generate_professors_by_department_report()
        elif report_type == "Materias por Carrera":
            self.generate_courses_by_department_report()
        elif report_type == "Record Academico":
            self.generate_record_academico_report()
        elif report_type == "Constancia de Estudio":
            self.generate_constancia_estudio_report()
        elif report_type == "Estudiantes por semestre":
            self.generate_students_by_semester_report()
        elif report_type == "Profesores por materias":
            self.generate_professors_by_courses_report()

    def generate_students_by_career_report(self):
        tk.Label(
            self.report_frame,
            text="Reporte: Estudiantes por Carrera",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 20))

        # --- CONSULTA A LA BASE DE DATOS ---
        resultados = database.get_estudiantes_por_carrera()

        carreras_fijas = [
            "Ingeniería en Sistemas",
            "Ingeniería Mecánica",
            "Ingeniería Naval",
            "Enfermería",
        ]
        valores_dict = {carrera: 0 for carrera in carreras_fijas}
        for row in resultados:
            if row[0] in valores_dict:
                valores_dict[row[0]] = row[1]
        carreras = carreras_fijas
        valores = [valores_dict[c] for c in carreras_fijas]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(
            carreras,
            valores,
            color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c"],
        )
        ax.set_ylabel("Cantidad de Estudiantes")
        ax.set_title("Distribución de Estudiantes por Carrera")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        table_frame = tk.Frame(self.report_frame, bg="white", pady=20)
        table_frame.pack(fill="x")

        columns = ("carrera", "cantidad", "porcentaje")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=100, anchor="center")

        total = sum(valores)
        for i, carrera in enumerate(carreras):
            porcentaje = f"{(valores[i] / total) * 100:.2f}%" if total > 0 else "0.00%"
            tree.insert("", "end", values=(carrera, valores[i], porcentaje))
        tree.pack(fill="x")

        if hasattr(self, "export_btn") and self.export_btn.winfo_exists():
            self.export_btn.destroy()
        if self.report_combo.get() == "Estudiantes por Carrera":
            self.export_btn = tk.Button(
                self.report_combo.master,
                text="Exportar a PDF",
                bg="#3498db",
                fg="white",
                font=("Arial", 10, "bold"),
                bd=0,
                padx=15,
                pady=5,
                command=lambda: self.pdf_EstudiantesPorCarreras(
                    carreras, valores, self.user.nombre
                ),
            )
            self.export_btn.pack(side="left", padx=10)

    def pdf_EstudiantesPorCarreras(self, carreras, valores, usuario):
        try:
            # Abrir diálogo para guardar archivo
            file_path = filedialog.asksaveasfilename(
                initialfile="estudiantes_por_carrera.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar Reporte como PDF",
            )
            if not file_path:
                return  # El usuario canceló

            reportesPDF.estudiantesPorCarrera(
                self, carreras, valores, file_path, usuario
            )

            messagebox.showinfo("Éxito", "El reporte se exportó correctamente a PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte a PDF:\n{e}")

    def generate_professors_by_department_report(self):
        # Implementación del reporte de profesores por departamento
        tk.Label(
            self.report_frame,
            text="Reporte: Profesores por Carrera",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 20))

        # --- CONSULTA A LA BASE DE DATOS ---
        resultados = database.get_profesores_por_carrera()

        carreras_fijas = [
            "Ingeniería en Sistemas",
            "Ingeniería Mecánica",
            "Ingeniería Naval",
            "Enfermería",
        ]
        valores_dict = {carrera: 0 for carrera in carreras_fijas}
        for row in resultados:
            if row[0] in valores_dict:
                valores_dict[row[0]] = row[1]
        carreras = carreras_fijas
        valores = [valores_dict[c] for c in carreras_fijas]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(
            carreras,
            valores,
            color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c"],
        )
        ax.set_ylabel("Cantidad de Profesores")
        ax.set_title("Distribución de Profesores por Carrera")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        table_frame = tk.Frame(self.report_frame, bg="white", pady=20)
        table_frame.pack(fill="x")

        columns = ("carrera", "cantidad", "porcentaje")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=100, anchor="center")

        total = sum(valores)
        for i, carrera in enumerate(carreras):
            porcentaje = f"{(valores[i] / total) * 100:.2f}%" if total > 0 else "0.00%"
            tree.insert("", "end", values=(carrera, valores[i], porcentaje))
        tree.pack(fill="x")

        if hasattr(self, "export_btn") and self.export_btn.winfo_exists():
            self.export_btn.destroy()
        if self.report_combo.get() == "Profesores por Carrera":
            self.export_btn = tk.Button(
                self.report_combo.master,
                text="Exportar a PDF",
                bg="#3498db",
                fg="white",
                font=("Arial", 10, "bold"),
                bd=0,
                padx=15,
                pady=5,
                command=lambda: self.pdf_ProfesoresPorCarreras(
                    carreras, valores, self.user.nombre
                ),
            )
            self.export_btn.pack(side="left", padx=10)

    def pdf_ProfesoresPorCarreras(self, carreras, valores, usuario):
        try:
            # Abrir diálogo para guardar archivo
            file_path = filedialog.asksaveasfilename(
                initialfile="profesores_por_carrera.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar Reporte como PDF",
            )
            if not file_path:
                return  # El usuario canceló

            reportesPDF.profesoresPorCarrera(
                self, carreras, valores, file_path, usuario
            )

            messagebox.showinfo("Éxito", "El reporte se exportó correctamente a PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte a PDF:\n{e}")

    def pdf_EstudiantesPorMateria(self, resultados, usuario):
        try:
            # Abrir diálogo para guardar archivo
            file_path = filedialog.asksaveasfilename(
                initialfile="estudiantes_por_materia.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar Reporte como PDF",
            )
            if not file_path:
                return  # El usuario canceló
            reportesPDF.estudiantesPorMaterias(self, resultados, file_path, usuario)

            messagebox.showinfo("Éxito", "El reporte se exportó correctamente a PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte a PDF:\n{e}")

    def generate_students_by_courses_report(self):
        # Implementación del reporte de estudiantes por materia

        tk.Label(
            self.report_frame,
            text="Reporte: Estudiantes por Materia",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 20))

        # Llamada a la función del database
        resultados = database.get_estudiantes_nombres_y_cantidad_por_materia()
        # Ordenar por materia
        resultados.sort(key=lambda x: x[0])
        print(resultados)

        columns = ("materia", "estudiante", "cantidad")
        tree = ttk.Treeview(
            self.report_frame, columns=columns, show="headings", height=15
        )
        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, width=150, anchor="center")

        materia_actual = None
        for materia, estudiante, cantidad in resultados:
            if materia != materia_actual:
                # Fila de encabezado para la nueva materia
                tree.insert(
                    "", "end", values=(f"Materia: {materia}", "", f"Total: {cantidad}")
                )
                materia_actual = materia
            tree.insert("", "end", values=("", estudiante, ""))

        tree.pack(fill="x")
        if hasattr(self, "export_btn") and self.export_btn.winfo_exists():
            self.export_btn.destroy()
        if self.report_combo.get() == "Estudiantes por Materia":
            self.export_btn = tk.Button(
                self.report_combo.master,
                text="Exportar a PDF",
                bg="#3498db",
                fg="white",
                font=("Arial", 10, "bold"),
                bd=0,
                padx=15,
                pady=5,
                command=lambda: self.pdf_EstudiantesPorMateria(
                    resultados, self.user.nombre
                ),
            )
            self.export_btn.pack(side="left", padx=10)

    def generate_courses_by_department_report(self):
        tk.Label(
            self.report_frame,
            text="Reporte: Materias por Carrera",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(0, 20))

        # Obtener carreras y contar materias por carrera
        carreras = database.get_carreras()
        valores = []
        materias_por_carrera = {}
        with database.get_db_connection() as conn:
            cursor = conn.cursor()
            for carrera in carreras:
                cursor.execute(
                    """
                    SELECT codigo, nombre, semestre
                    FROM materias
                    WHERE carrera = ?
                    ORDER BY semestre, nombre
                    """,
                    (carrera,),
                )
                materias = cursor.fetchall()
                materias_por_carrera[carrera] = materias
                valores.append(len(materias))

        # --- GRAFICA ---
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(
            carreras,
            valores,
            color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c"][: len(carreras)],
        )
        ax.set_ylabel("Cantidad de Materias")
        ax.set_title("Distribución de Materias por Carrera")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # --- TABLA RESUMEN ---
        table_frame = tk.Frame(self.report_frame, bg="white", pady=20)
        table_frame.pack(fill="x")

        columns = ("carrera", "cantidad")
        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=len(carreras)
        )
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=180, anchor="center")

        for i, carrera in enumerate(carreras):
            tree.insert("", "end", values=(carrera, valores[i]))
        tree.pack(fill="x")

        # Botón de exportar a PDF
        if hasattr(self, "export_btn") and self.export_btn.winfo_exists():
            self.export_btn.destroy()
        if self.report_combo.get() == "Materias por Carrera":
            self.export_btn = tk.Button(
                self.report_combo.master,
                text="Exportar a PDF",
                bg="#3498db",
                fg="white",
                font=("Arial", 10, "bold"),
                bd=0,
                padx=15,
                pady=5,
                command=lambda: self.pdf_MateriasPorCarrera(self.user.nombre),
            )
            self.export_btn.pack(side="left", padx=10)

    def pdf_MateriasPorCarrera(self, usuario):
        try:
            file_path = filedialog.asksaveasfilename(
                initialfile="materias_por_carrera.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar Reporte como PDF",
            )
            if not file_path:
                return  # El usuario canceló

            reportesPDF.materiasPorCarrera(self, file_path, usuario)

            messagebox.showinfo("Éxito", "El reporte se exportó correctamente a PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte a PDF:\n{e}")

    def generate_record_academico_report(self):
        from models.student import Student
        from tkinter import filedialog, messagebox
        import os
        import traceback
        from config import database

        # 1. Obtener información del estudiante
        estudiante = Student.get_by_user_id(self.user.id)
        if not estudiante:
            messagebox.showerror("Error", "No se encontró información del estudiante.")
            return

        # 2. Preparar datos del estudiante para el PDF
        student_data = {
            "cedula": self.user.cedula,
            "nombre": self.user.nombre,
            "apellido": self.user.apellido,
            "carrera": estudiante.carrera,
            "semestre": estudiante.semestre,
        }

        # 3. Consultar el historial académico usando la función del database
        try:
            academic_records = database.get_record_academico_by_student_id(
                estudiante.id
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo obtener el historial académico:\n{e}"
            )
            return

        # 4. Pedir ruta para guardar el PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"record_academico_{self.user.cedula}.pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Record Académico como PDF",
        )
        if not file_path:
            return

        # 5. Llamar a la función de generación de PDF
        try:
            reportesPDF.generate_record_academico_report(
                file_path,
                student_data,
                academic_records,
                self.user.nombre + " " + self.user.apellido,
            )
            messagebox.showinfo(
                "Éxito", "El record académico se exportó correctamente a PDF."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo exportar el record académico a PDF:\n{e}\n{traceback.format_exc()}",
            )

    def generate_constancia_estudio_report(self):
        from models.student import Student
        from tkinter import filedialog, messagebox
        import os
        import traceback
        from config import database

        # 1. Obtener información del estudiante
        estudiante = Student.get_by_user_id(self.user.id)
        if not estudiante:
            messagebox.showerror("Error", "No se encontró información del estudiante.")
            return

        # 2. Preparar datos del estudiante para el PDF
        student_data = {
            "cedula": self.user.cedula,
            "nombre": self.user.nombre,
            "apellido": self.user.apellido,
            "carrera": estudiante.carrera,
            "semestre": estudiante.semestre,
        }

        # 3. Pedir ruta para guardar el PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"constancia_estudio_{self.user.cedula}.pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Constancia de Estudio como PDF",
        )
        if not file_path:
            return

        # 4. Llamar a la función de generación de PDF
        try:
            reportesPDF.generate_constancia_estudio_report(
                file_path,
                student_data,
                self.user.nombre + " " + self.user.apellido,
            )
            messagebox.showinfo(
                "Éxito", "La constancia de estudio se exportó correctamente a PDF."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo exportar la constancia de estudio a PDF:\n{e}\n{traceback.format_exc()}",
            )

    def generate_students_by_semester_report(self):
        from models.coordinator import Coordinator
        from tkinter import filedialog, messagebox
        import os
        import traceback
        from config import database

        # 1. Obtener información del coordinador
        coordinador = Coordinator.get_by_id(self.user.id)
        if not coordinador:
            messagebox.showerror("Error", "No se encontró información del coordinador.")
            return

        if not coordinador.carrera:
            messagebox.showerror(
                "Error", "El coordinador no tiene una carrera asignada."
            )
            return

        # 2. Obtener estudiantes por semestre filtrados por carrera
        try:
            estudiantes_por_semestre = (
                database.get_estudiantes_por_semestre_por_carrera(coordinador.carrera)
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {str(e)}")
            return

        if not estudiantes_por_semestre:
            messagebox.showinfo(
                "Información",
                f"No hay estudiantes registrados en la carrera {coordinador.carrera}.",
            )
            return

        # 3. Solicitar ubicación para guardar el PDF
        carrera_safe = (
            coordinador.carrera.replace(" ", "_")
            if coordinador.carrera
            else "Sin_Carrera"
        )
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Reporte de Estudiantes por Semestre",
            initialfile=f"Estudiantes_por_Semestre_{carrera_safe}_{datetime.now().strftime('%Y%m%d')}.pdf",
        )

        if not file_path:
            return

        # 4. Generar el PDF
        try:
            from pdf import reportesPDF

            reportesPDF.generate_students_by_semester_report(
                file_path=file_path,
                students_by_semester=estudiantes_por_semestre,
                carrera=coordinador.carrera,
                usuario=self.user.nombre + " " + self.user.apellido,
            )
            messagebox.showinfo(
                "Éxito", f"Reporte generado exitosamente en:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")
            print(f"Error completo: {traceback.format_exc()}")

    def generate_professors_by_courses_report(self):
        from models.coordinator import Coordinator
        from tkinter import filedialog, messagebox
        import os
        import traceback
        from config import database

        # 1. Obtener información del coordinador
        coordinador = Coordinator.get_by_id(self.user.id)
        if not coordinador:
            messagebox.showerror("Error", "No se encontró información del coordinador.")
            return

        if not coordinador.carrera:
            messagebox.showerror(
                "Error", "El coordinador no tiene una carrera asignada."
            )
            return

        # 2. Obtener profesores por materias filtrados por carrera
        try:
            profesores_por_materias = database.get_profesores_por_materias_por_carrera(
                coordinador.carrera
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {str(e)}")
            return

        if not profesores_por_materias:
            messagebox.showinfo(
                "Información",
                f"No hay materias registradas en la carrera {coordinador.carrera}.",
            )
            return

        # 3. Solicitar ubicación para guardar el PDF
        carrera_safe = (
            coordinador.carrera.replace(" ", "_")
            if coordinador.carrera
            else "Sin_Carrera"
        )
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Reporte de Profesores por Materias",
            initialfile=f"Profesores_por_Materias_{carrera_safe}_{datetime.now().strftime('%Y%m%d')}.pdf",
        )

        if not file_path:
            return

        # 4. Generar el PDF
        try:
            from pdf import reportesPDF

            reportesPDF.generate_professors_by_courses_report(
                file_path=file_path,
                professors_by_courses=profesores_por_materias,
                carrera=coordinador.carrera,
                usuario=self.user.nombre + " " + self.user.apellido,
            )
            messagebox.showinfo(
                "Éxito", f"Reporte generado exitosamente en:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")
            print(f"Error completo: {traceback.format_exc()}")
