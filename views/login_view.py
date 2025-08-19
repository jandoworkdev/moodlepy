import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class LoginView(ttk.Frame):
    """Pantalla de Login"""

    def __init__(self, parent, api_client, on_success):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.pack(fill="both", expand=True)

        # Título
        title = ttk.Label(
            self,
            text="🔐 Iniciar Sesión en Moodle",
            font=("Segoe UI", 18, "bold"),
            foreground="#0d6efd"
        )
        title.pack(pady=20)

        # Usuario
        ttk.Label(self, text="Usuario:", font=("Segoe UI", 12)).pack(pady=5)
        self.entry_user = ttk.Entry(self, width=30)
        self.entry_user.pack(pady=5)

        # Contraseña
        ttk.Label(self, text="Contraseña:", font=("Segoe UI", 12)).pack(pady=5)
        self.entry_pass = ttk.Entry(self, width=30, show="*")
        self.entry_pass.pack(pady=5)

        # Botón login
        btn = ttk.Button(
            self, text="Ingresar", bootstyle=PRIMARY, command=self.try_login
        )
        btn.pack(pady=15)

        # Mensaje feedback
        self.lbl_status = ttk.Label(self, text="", font=("Segoe UI", 10))
        self.lbl_status.pack(pady=5)

    def try_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        self.lbl_status.config(text="⏳ Validando credenciales...")

        success = self.api.login(user, pwd)

        if success:
            self.lbl_status.config(text="✅ Login exitoso", foreground="green")
            self.destroy()
            self.on_success()
        else:
            self.lbl_status.config(
                text="❌ Usuario o contraseña incorrectos", foreground="red"
            )
