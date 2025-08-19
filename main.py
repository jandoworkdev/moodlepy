import ttkbootstrap as ttk
from moodle_api import MoodleAPI
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.categories_view import CategoriesView
from views.courses_view import CoursesView
from sidebar import Sidebar


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("MoodlePy")
        self.geometry("1000x600")

        self.api_client = MoodleAPI()
        LoginView(self, self.api_client, on_success=self.show_main)

    def show_main(self):
        """Renderiza la app principal después del login"""
        for widget in self.winfo_children():
            widget.destroy()

        # Sidebar
        self.sidebar = Sidebar(self, self.show_view)

        # Contenedor principal (para vistas)
        self.container = ttk.Frame(self)
        self.container.pack(side="right", fill="both", expand=True)

        self.current_view = None
        self.show_view("dashboard")

    def show_view(self, view_name):
        """Muestra la vista seleccionada en el contenedor"""
        if self.current_view:
            self.current_view.destroy()

        if view_name == "dashboard":
            self.current_view = DashboardView(self.container, self.api_client)
        elif view_name == "categories":
            self.current_view = CategoriesView(self.container, self.api_client)
        elif view_name == "courses":
            self.current_view = CoursesView(self.container, self.api_client)
        else:
            self.current_view = ttk.Label(self.container, text="Vista no encontrada")

        self.current_view.pack(fill="both", expand=True)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
