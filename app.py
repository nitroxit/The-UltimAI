import customtkinter as ctk
from main_page import MainPage
from label_page import LabelPage
from train_page import TrainPage
from train_from_video import TrainFromVideoPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ai model creator")
        self.geometry("900x700")  # Default geometry

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        for PageClass in (MainPage, LabelPage, TrainPage, TrainFromVideoPage):
            page = PageClass(parent=self.container, controller=self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("MainPage")

    def show_page(self, page_name):
        page = self.pages[page_name]

        # Check if the page specifies a preferred geometry
        if hasattr(page, "preferred_geometry"):
            self.geometry(page.preferred_geometry)

        # Show the page
        page.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
