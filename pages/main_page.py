import customtkinter as ctk
from tkinter import Tk

class MainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.preferred_geometry = "350x250"


        ctk.CTkLabel(self, text="Main Menu", font=("Arial", 16)).pack(pady=20)

        ctk.CTkButton(self, text="Label", command=lambda: controller.show_page("LabelPage")).pack(pady=10)
        ctk.CTkButton(self, text="Train", command=lambda: controller.show_page("TrainPage")).pack(pady=10)
        ctk.CTkButton(self, text="SS Tool", command=lambda: controller.show_page("SSPage")).pack(pady=10)
