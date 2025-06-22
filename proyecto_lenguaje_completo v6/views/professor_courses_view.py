import tkinter as tk
from tkinter import ttk, messagebox
from controllers.section_controller import SectionController
from models.professor import Professor


class ProfessorCoursesView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.section_controller = SectionController()
        self.create_widgets()

    def create_widgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.parent, bg="white", height=60)
        header_frame.pack(fill="x")

        header_title = tk.Label(
            header_frame,
            text="Mis Materias",
            font=("Arial", 16, "bold"),
            bg="white",
        )
        header_title.pack(side="left", padx=20, pady=15)

        # Obtener el id_profesor a partir del usuario logueado
        profesor = Professor.get_by_user_id(self.user.id)
        if not profesor:
            tk.Label(
                self.parent, text="No se encontró información del profesor.", fg="red"
            ).pack(pady=20)
            return

        # Obtener las secciones/materias que imparte el profesor
        secciones = self.section_controller.get_by_professor(profesor.id)

        # Tabla de materias
        columns = ("nombre_materia", "periodo", "aula", "seccion", "estudiantes")
        table_frame = tk.Frame(self.parent, bg="white")
        table_frame.pack(fill="both", expand=True, padx=40, pady=30)

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20,
        )
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Encabezados
        tree.heading("nombre_materia", text="Materia")
        tree.heading("periodo", text="Período")
        tree.heading("aula", text="Aula")
        tree.heading("seccion", text="Sección")
        tree.heading("estudiantes", text="Estudiantes")

        tree.column("nombre_materia", width=200, anchor="center")
        tree.column("periodo", width=100, anchor="center")
        tree.column("aula", width=80, anchor="center")
        tree.column("seccion", width=80, anchor="center")
        tree.column("estudiantes", width=100, anchor="center")

        # Insertar datos
        for seccion in secciones:
            # seccion: (id_seccion, nombre_materia, periodo, aula, estudiantes)
            tree.insert(
                "",
                "end",
                values=(
                    seccion[0],  # nombre_materia
                    seccion[1],  # periodo
                    seccion[2],  # aula
                    seccion[3],  # sección (número de sección)
                    seccion[4],  # estudiantes
                ),
            )

        if not secciones:
            tk.Label(
                self.parent, text="No tienes materias asignadas actualmente.", fg="gray"
            ).pack(pady=20)
