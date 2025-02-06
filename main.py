from db.database import init_db
import flet as ft
from ui.views import main_view

if __name__ == "__main__":
    init_db()
    ft.app(target=main_view)
