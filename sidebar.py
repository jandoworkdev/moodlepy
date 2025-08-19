import ttkbootstrap as ttk


class Sidebar(ttk.Frame):
    """Sidebar lateral con navegación"""

    def __init__(self, parent, on_nav):
        super().__init__(parent)
        self.on_nav = on_nav
        self.pack(side="left", fill="y")

        # Botones de menú
        self.btn_dashboard = ttk.Button(
            self, text="📊 Dashboard", command=lambda: self.on_nav("dashboard")
        )
        self.btn_dashboard.pack(fill="x", pady=5, padx=5)

        self.btn_categories = ttk.Button(
            self, text="📂 Categorías", command=lambda: self.on_nav("categories")
        )
        self.btn_categories.pack(fill="x", pady=5, padx=5)

        self.btn_courses = ttk.Button(
            self, text="📘 Cursos", command=lambda: self.on_nav("courses")
        )
        self.btn_courses.pack(fill="x", pady=5, padx=5)

        self.btn_excel = ttk.Button(
            self, text="📑 Excel", command=lambda: self.on_nav("excel")
        )
        self.btn_excel.pack(fill="x", pady=5, padx=5)
