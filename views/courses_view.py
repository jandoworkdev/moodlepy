import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CoursesView(ttk.Frame):
    """Vista de cursos"""

    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api = api_client

        title = ttk.Label(
            self,
            text="📘 Lista de Cursos",
            font=("Segoe UI", 18, "bold"),
            foreground="#0d6efd"
        )
        title.pack(pady=20)

        cols = ("ID", "Código", "Nombre")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", bootstyle=PRIMARY)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=250, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=25, pady=15)

        btn = ttk.Button(self, text="🔄 Cargar Cursos", bootstyle=INFO, command=self.load_courses)
        btn.pack(pady=10)

    def load_courses(self):
        self.tree.delete(*self.tree.get_children())
        data = self.api.get_courses()
        if "error" in data:
            self.tree.insert("", "end", values=("Error", data["error"], ""))
            return
        for course in data:
            self.tree.insert("", "end", values=(course["id"], course["shortname"], course["fullname"]))
