# excel_view.py
# Vista para subir y mostrar valores de un archivo Excel

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd


class ExcelView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.df = None
        self.filter_vars = {}
        self.create_widgets()

    def create_widgets(self):
        self.upload_btn = tk.Button(self, text="Subir archivo Excel", command=self.upload_file)
        self.upload_btn.pack(pady=10)

        self.filters_frame = tk.Frame(self)
        self.filters_frame.pack(fill="x", padx=10, pady=5)

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = None

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.show_table_with_filters()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def show_table_with_filters(self):
        # Limpiar filtros y tabla previos
        for widget in self.filters_frame.winfo_children():
            widget.destroy()
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if self.df is None or self.df.empty:
            return

        # Crear filtros por columna
        self.filter_vars = {}
        for idx, col in enumerate(self.df.columns):
            lbl = tk.Label(self.filters_frame, text=col)
            lbl.grid(row=0, column=idx, padx=2, pady=2)
            var = tk.StringVar()
            ent = tk.Entry(self.filters_frame, textvariable=var, width=12)
            ent.grid(row=1, column=idx, padx=2, pady=2)
            var.trace_add('write', self.apply_filters)
            self.filter_vars[col] = var

        # Crear tabla
        self.tree = ttk.Treeview(self.table_frame, columns=list(self.df.columns), show="headings")
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.update_table(self.df)

    def update_table(self, df):
        # Limpiar tabla
        if self.tree is not None:
            for row in self.tree.get_children():
                self.tree.delete(row)
            # Insertar filas
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=list(row))

    def apply_filters(self, *args):
        if self.df is None:
            return
        filtered_df = self.df.copy()
        for col, var in self.filter_vars.items():
            val = var.get().strip()
            if val:
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]
        self.update_table(filtered_df)

# Para pruebas independientes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Subir y mostrar Excel")
    app = ExcelView(master=root)
    app.mainloop()
