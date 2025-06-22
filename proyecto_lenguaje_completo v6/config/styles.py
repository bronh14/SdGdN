from tkinter import ttk


def configure_styles():
    """Configura los estilos de la aplicación."""
    style = ttk.Style()
    style.theme_use("clam")

    # Botones
    style.configure("TButton", padding=6, relief="flat")
    style.configure("Primary.TButton", background="#3498db", foreground="white")
    style.configure("Success.TButton", background="#2ecc71", foreground="white")
    style.configure("Danger.TButton", background="#e74c3c", foreground="white")
    style.configure("Warning.TButton", background="#f39c12", foreground="white")

    # Frames
    style.configure("Secondary.TFrame", background="#2c3e50")

    # Botones de sidebar
    style.configure(
        "Sidebar.TButton",
        width=20,
        anchor="w",
        padding=10,
        background="#2c3e50",
        foreground="white",
    )
    style.map(
        "Sidebar.TButton", background=[("active", "#3498db"), ("pressed", "#2980b9")]
    )

    return style
