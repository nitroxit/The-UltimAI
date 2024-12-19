import customtkinter as ctk
from pages.main_page import MainPage
from pages.label_page import LabelPage
from pages.train_page import TrainPage
from pages.ss_page import SSPage

screenshot_tool_active = False
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # Base theme for synthwave vibes

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.pages = {}  # Store pages here
        self.title("AI Model Creator")
        self.geometry("900x700")  # Default geometry
        self.configure(bg="#1a1a2e")

        # Configure grid to center-align the container in the main window
        self.grid_rowconfigure(0, weight=1)  # Center vertically
        self.grid_columnconfigure(0, weight=1)  # Center horizontally

        # Create a container frame
        self.container = ctk.CTkFrame(self, fg_color="#0f0f1f")
        self.container.grid(row=0, column=0, sticky="nsew")  # Center-align the container

        # Configure grid inside the container to center-align pages
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}

        for PageClass in (MainPage, LabelPage, TrainPage, SSPage):
            page = PageClass(parent=self.container, controller=self)
            self.pages[PageClass.__name__] = page
            # Center-align the page within the container
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("MainPage")

    def show_page(self, page_name):
        if page_name not in self.pages:
            print(f"Error: Page '{page_name}' does not exist.")
            return
        page = self.pages[page_name]
        if hasattr(page, "preferred_geometry"):
            self.geometry(page.preferred_geometry)
        page.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
