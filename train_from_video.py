import customtkinter as ctk

class TrainFromVideoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ctk.CTkLabel(self, text="Train from Video Page", font=("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self, text="Back to Main Menu", command=lambda: controller.show_page("MainPage")).pack(pady=10)
