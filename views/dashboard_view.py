import ttkbootstrap as ttk
from ttkbootstrap.constants import PRIMARY


class DashboardView(ttk.Frame):
    """Vista principal de dashboard"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api = api_client

        title = ttk.Label(
            self,
            text="📊 Bienvenido al Dashboard",
            font=("Segoe UI", 18, "bold"),
            foreground="#0d6efd"
        )
        title.pack(pady=20)

        desc = ttk.Label(
            self,
            text="Aquí verás métricas generales de Moodle.",
            font=("Segoe UI", 12)
        )
        desc.pack(pady=10)
