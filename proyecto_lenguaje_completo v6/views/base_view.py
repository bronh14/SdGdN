import tkinter as tk


class BaseView:
    """Clase base para todas las vistas."""

    def __init__(self, parent, app_controller):
        self.parent = parent
        self.app_controller = app_controller
        self.frame = tk.Frame(parent)
        self.frame.pack(expand=True, fill="both")

    def create_widgets(self):
        """Método a implementar en las clases hijas."""
        pass

    def destroy(self):
        """Destruye la vista actual."""
        self.frame.destroy()
