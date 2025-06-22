import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView
from views.auth_views import LoginView, RegisterView
from config.styles import configure_styles
from config.inscripcion import get_inscripcion_habilitada


class WelcomeView(BaseView):
    def __init__(self, parent, app_controller):
        super().__init__(parent, app_controller)
        self.frame.configure(bg="#f0f0f0")

        # Configurar estilos
        self.style = configure_styles()

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Banner superior
        banner_frame = tk.Frame(self.frame, bg="#2c3e50", height=150)
        banner_frame.pack(fill="x")

        title_label = tk.Label(
            banner_frame,
            text="Sistema de Gestión Académica",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Contenido central
        content_frame = tk.Frame(self.frame, bg="#f0f0f0")
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)

        # Opciones
        options_frame = tk.Frame(content_frame, bg="#f0f0f0")
        options_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título de bienvenida
        welcome_label = tk.Label(
            options_frame,
            text="¡Bienvenido al Sistema!",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
        )
        welcome_label.pack(pady=20)

        # Botones
        btn_login = ttk.Button(
            options_frame,
            text="Iniciar Sesión",
            style="Primary.TButton",
            width=25,
            command=self.show_login,
        )
        btn_login.pack(pady=10)

        if get_inscripcion_habilitada():
            btn_register = ttk.Button(
                options_frame,
                text="Registrarse",
                style="Success.TButton",
                width=25,
                command=self.show_register,
            )
            btn_register.pack(pady=10)

        btn_exit = ttk.Button(
            options_frame,
            text="Salir",
            style="Danger.TButton",
            width=25,
            command=self.parent.quit,
        )
        btn_exit.pack(pady=10)

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

    def show_login(self):
        # Destruir la vista actual
        self.destroy()

        # Crear y mostrar la vista de login
        login_view = LoginView(self.parent, self.app_controller)

    def show_register(self):
        # Destruir la vista actual
        self.destroy()

        # Crear y mostrar la vista de registro
        register_view = RegisterView(self.parent, self.app_controller)
