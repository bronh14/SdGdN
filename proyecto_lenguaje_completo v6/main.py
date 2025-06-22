import tkinter as tk
from views.welcome_view import WelcomeView
from config.database import initialize_database
from config.styles import configure_styles
from views.dashboard_view import DashboardView


class AcademicSystemApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión Académica")
        self.root.geometry("1200x800")
        self.root.state("zoomed")
        # Activar pantalla completa
        # self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#f8f9fa")

        # Inicializar la base de datos
        initialize_database()

        # Configurar estilos
        self.style = configure_styles()

        # Mostrar la vista de bienvenida
        self.current_view = None
        self.current_user = None
        self.show_welcome()

    def show_welcome(self):
        # Limpiar la vista actual si existe
        if self.current_view:
            self.current_view.destroy()

        # Crear y mostrar la vista de bienvenida
        self.current_view = WelcomeView(self.root, self)

    def show_main_interface(self, user):
        # Guardar el usuario actual
        self.current_user = user

        # Limpiar la vista actual si existe
        for widget in self.root.winfo_children():
            widget.destroy()

        # Crear y mostrar el dashboard
        self.current_view = DashboardView(self.root, self, user)

    def logout(self):
        self.current_user = None
        self.show_welcome()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AcademicSystemApp()
    app.run()
