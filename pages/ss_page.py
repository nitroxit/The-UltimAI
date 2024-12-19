import customtkinter as ctk

class SSPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.preferred_geometry="300x300"

        ctk.CTkLabel(self, text="Screen Shot Tool Page", font=("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self, text="Back to Main Menu", command=lambda: controller.show_page("MainPage")).pack(pady=10)
