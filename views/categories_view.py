import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CategoriesView(ttk.Frame):
    """Vista de categorías"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api = api_client

        title = ttk.Label(
            self,
            text="📂 Categorías de Moodle",
            font=("Segoe UI", 18, "bold"),
            foreground="#0d6efd"
        )
        title.pack(pady=20)

        # Placeholder
        msg = ttk.Label(self, text="Aquí se mostrarán las categorías.", font=("Segoe UI", 12))
        msg.pack(pady=10)
