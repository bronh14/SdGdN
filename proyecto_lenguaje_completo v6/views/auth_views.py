import threading
import tkinter as tk
import time
from tkinter import ttk, messagebox
from config.database import get_connection, get_db_connection
from views.base_view import BaseView
from controllers.auth_controller import AuthController
from config.styles import configure_styles


class LoginView(BaseView):
    def __init__(self, parent, app_controller):
        super().__init__(parent, app_controller)
        self.frame.configure(bg="#f0f0f0")
        self.auth_controller = AuthController()

        # Configurar estilos
        self.style = configure_styles()

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Banner superior
        banner_frame = tk.Frame(self.frame, bg="#2c3e50", height=100)
        banner_frame.pack(fill="x")

        title_label = tk.Label(
            banner_frame,
            text="Iniciar Sesión",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Contenido central
        content_frame = tk.Frame(self.frame, bg="#f0f0f0")
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)

        # Formulario
        self.form_frame = tk.Frame(content_frame, bg="white", padx=30, pady=30)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center", width=400)

        # Logo o ícono
        logo_label = tk.Label(
            self.form_frame, text="🎓", font=("Arial", 48), bg="white"
        )
        logo_label.pack(pady=(0, 20))

        # Campos del formulario
        self.cedula_label = tk.Label(
            self.form_frame, text="Cédula:", font=("Arial", 12), bg="white"
        )
        self.cedula_label.pack(anchor="w", pady=(10, 5))
        self.cedula_entry = ttk.Entry(self.form_frame, font=("Arial", 12), width=30)
        self.cedula_entry.pack(fill="x", pady=(0, 10))

        self.password_label = tk.Label(
            self.form_frame, text="Contraseña:", font=("Arial", 12), bg="white"
        )
        self.password_label.pack(anchor="w", pady=(10, 5))
        self.password_entry = ttk.Entry(
            self.form_frame, font=("Arial", 12), width=30, show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))

        # tk.Label(form_frame, text="Cédula:", font=("Arial", 12), bg="white").pack(
        #     anchor="w", pady=(10, 5)
        # )
        # self.cedula_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        # self.cedula_entry.pack(fill="x", pady=(0, 10))

        # tk.Label(form_frame, text="Contraseña:", font=("Arial", 12), bg="white").pack(
        #     anchor="w", pady=(10, 5)
        # )
        # self.password_entry = tk.Entry(
        #     form_frame, font=("Arial", 12), width=30, show="*"
        # )
        # self.password_entry.pack(fill="x", pady=(0, 20))

        # Botones
        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.pack(pady=10)

        btn_login = ttk.Button(
            btn_frame,
            text="Iniciar Sesión",
            style="Primary.TButton",
            width=15,
            command=self.login,
        )
        btn_login.pack(side="left", padx=10)

        btn_cancel = ttk.Button(
            btn_frame,
            text="Cancelar",
            style="Danger.TButton",
            width=15,
            command=self.cancel,
        )
        btn_cancel.pack(side="left", padx=10)

        # Footer
        footer_frame = tk.Frame(self.frame, bg="#2c3e50", height=50)
        footer_frame.pack(fill="x", side="bottom")

        footer_label = tk.Label(
            footer_frame,
            text="© 2025 Sistema de Gestión Académica",
            fg="white",
            bg="#2c3e50",
        )
        footer_label.place(relx=0.5, rely=0.5, anchor="center")

    def login(self):
        """Procesa el inicio de sesión."""
        cedula = self.cedula_entry.get()
        password = self.password_entry.get()

        try:
            time.sleep(1)  # Simular llamada a la red
            user = self.auth_controller.login(cedula, password)
            if user:
                self.frame.after(0, self.handle_login_success, user)
                # messagebox.showinfo("Éxito", f"Bienvenido, {user.get_full_name()}")
                # Mostrar la interfaz principal
                # self.app_controller.show_main_interface(user)
            else:
                messagebox.showerror("Error", "Cédula o contraseña incorrectos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {str(e)}")

    def handle_login_success(self, user):
        """Maneja la UI para un login exitoso."""
        # Limpiar toda la ventana para una pantalla limpia
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Contenedor para el feedback de éxito en el centro
        feedback_container = tk.Frame(self.frame, bg="#f0f0f0")
        feedback_container.place(relx=0.5, rely=0.5, anchor="center")

        # Icono de éxito (restaurado al original)
        success_icon_label = tk.Label(
            feedback_container, text="✅", font=("Arial", 80), fg="green", bg="#f0f0f0"
        )
        success_icon_label.pack(pady=(0, 10))

        # Mensaje de bienvenida (restaurado al original)
        self.welcome_message = f"Bienvenido, {user.get_full_name()}"
        self.welcome_label = tk.Label(
            feedback_container,
            text=self.welcome_message,
            font=("Arial", 16),
            fg="black",
            bg="#f0f0f0",
        )
        self.welcome_label.pack()

        self._animate_logout_message(0)
        # Transición al dashboard después de 2 segundos
        self.frame.after(2000, self.app_controller.show_main_interface, user)

    def _animate_logout_message(self, dot_count):
        """Anima los puntos suspensivos en el mensaje de cierre de sesión."""
        # Si el widget todavía existe, actualiza el texto
        if self.welcome_label.winfo_exists():
            # Construir el texto con el número actual de puntos
            new_text = f"{self.welcome_message}{'.' * (dot_count % 4)}"
            self.welcome_label.config(text=new_text)

            # Programar la próxima actualización
            self.frame.after(400, self._animate_logout_message, dot_count + 1)

    def cancel(self):
        """Cancela el inicio de sesión y vuelve a la pantalla de bienvenida."""
        self.destroy()
        self.app_controller.show_welcome()


class RegisterView(BaseView):
    def __init__(self, parent, app_controller):
        super().__init__(parent, app_controller)
        self.frame.configure(bg="#f0f0f0")
        self.auth_controller = AuthController()

        # Configurar estilos
        self.style = configure_styles()

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Banner superior
        banner_frame = tk.Frame(self.frame, bg="#2c3e50", height=100)
        banner_frame.pack(fill="x")

        title_label = tk.Label(
            banner_frame,
            text="Registro de Usuario",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Contenido central
        content_frame = tk.Frame(self.frame, bg="#f0f0f0")
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)

        # Formulario
        self.form_frame = tk.Frame(content_frame, bg="white", padx=30, pady=30)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500)

        # Campos del formulario
        tk.Label(
            self.form_frame,
            text="Información Personal",
            font=("Arial", 14, "bold"),
            bg="white",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Campos del formulario

        # Cédula
        tk.Label(self.form_frame, text="Cédula:", font=("Arial", 12), bg="white").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.cedula_entry = tk.Entry(self.form_frame, font=("Arial", 12), width=30)
        self.cedula_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        # Nombre
        tk.Label(self.form_frame, text="Nombre:", font=("Arial", 12), bg="white").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.nombre_entry = tk.Entry(self.form_frame, font=("Arial", 12), width=30)
        self.nombre_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")

        # Apellido
        tk.Label(
            self.form_frame, text="Apellido:", font=("Arial", 12), bg="white"
        ).grid(row=3, column=0, sticky="w", pady=5)
        self.apellido_entry = tk.Entry(self.form_frame, font=("Arial", 12), width=30)
        self.apellido_entry.grid(row=3, column=1, pady=5, padx=10, sticky="w")

        # Contraseña
        tk.Label(
            self.form_frame, text="Contraseña:", font=("Arial", 12), bg="white"
        ).grid(row=4, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(
            self.form_frame, font=("Arial", 12), width=30, show="*"
        )
        self.password_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")

        # Confirmar Contraseña
        tk.Label(
            self.form_frame,
            text="Confirmar Contraseña:",
            font=("Arial", 12),
            bg="white",
        ).grid(row=5, column=0, sticky="w", pady=5)
        self.confirm_password_entry = tk.Entry(
            self.form_frame, font=("Arial", 12), width=30, show="*"
        )
        self.confirm_password_entry.grid(row=5, column=1, pady=5, padx=10, sticky="w")

        # Carrera (nuevo selector)
        tk.Label(self.form_frame, text="Carrera:", font=("Arial", 12), bg="white").grid(
            row=6, column=0, sticky="w", pady=5
        )
        # Obtener carreras únicas desde la base de datos
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT carrera FROM materias WHERE carrera IS NOT NULL"
            )
            carreras = [row[0] for row in cursor.fetchall()]
        self.carrera_combo = ttk.Combobox(
            self.form_frame,
            font=("Arial", 12),
            width=28,
            values=carreras,
            state="readonly",
        )
        self.carrera_combo.grid(row=6, column=1, pady=5, padx=10, sticky="w")
        if carreras:
            self.carrera_combo.current(3)  # Por defecto, la primera carrera

        # Botones
        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)

        btn_register = ttk.Button(
            btn_frame,
            text="Registrar",
            style="Success.TButton",
            width=15,
            command=self.register,
        )
        btn_register.pack(side="left", padx=10)

        btn_cancel = ttk.Button(
            btn_frame,
            text="Cancelar",
            style="Danger.TButton",
            width=15,
            command=self.cancel,
        )
        btn_cancel.pack(side="left", padx=10)

        # Footer
        footer_frame = tk.Frame(self.frame, bg="#2c3e50", height=50)
        footer_frame.pack(fill="x", side="bottom")

        footer_label = tk.Label(
            footer_frame,
            text="© 2025 Sistema de Gestión Académica",
            fg="white",
            bg="#2c3e50",
        )
        footer_label.place(relx=0.5, rely=0.5, anchor="center")

    def register(self):
        """Procesa el registro de usuario."""
        cedula = self.cedula_entry.get()
        nombre = self.nombre_entry.get().title()
        apellido = self.apellido_entry.get().title()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        carrera = self.carrera_combo.get()  # Obtener la carrera seleccionada
        rol = "alumno"  # Rol fijo como alumno

        try:
            user = self.auth_controller.register(
                cedula, nombre, apellido, password, confirm_password, rol, carrera
            )
            if user:
                messagebox.showinfo(
                    "Éxito", f"Usuario {nombre} {apellido} registrado correctamente"
                )
                self.destroy()
                self.app_controller.show_welcome()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar: {str(e)}")

    def cancel(self):
        """Cancela el registro y vuelve a la pantalla de bienvenida."""
        self.destroy()
        self.app_controller.show_welcome()
