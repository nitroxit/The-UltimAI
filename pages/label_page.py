import customtkinter as ctk
from tkinter import filedialog, Text  # Ensure Text is imported here
from PIL import Image, ImageTk
import os

class LabelPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.preferred_geometry = "900x700"

        self.controller = controller
        self.image_folder = None
        self.class_file = None
        self.images = []
        self.current_index = 0
        self.annotations = {}
        self.classes = []
        self.current_class = 0

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(main_frame, width=640, height=700)
        left_frame.grid(row=0, column=0, sticky="nsew")

        right_frame = ctk.CTkFrame(main_frame, width=200)
        right_frame.grid(row=0, column=1, sticky="nsew")

        self.canvas = ctk.CTkCanvas(left_frame, width=640, height=640, bg="gray")
        self.canvas.pack()

        self.image_name_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 14))
        self.image_name_label.pack(pady=5)

        ctk.CTkButton(right_frame, text="Choose Image Folder", command=self.choose_image_folder).pack(pady=10)
        ctk.CTkButton(right_frame, text="Choose Classes File", command=self.choose_class_file).pack(pady=10)
        ctk.CTkButton(right_frame, text="Back to Main Menu", command=lambda: controller.show_page("MainPage")).pack(pady=10)

        self.classes_listbox = Text(right_frame, width=30, height=20, state="disabled", wrap="none")
        self.classes_listbox.pack(pady=20)
        self.classes_listbox.bind("<Button-1>", self.select_class)

        self.start_x = None
        self.start_y = None
        self.temp_box = None
        self.temp_lines = []
        self.box_ids = []

    def choose_image_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_folder = folder_path
            self.images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if self.images:
                self.current_index = 0  # Reset to the first image
                self.display_image()

    def choose_class_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.class_file = file_path
            with open(file_path, "r") as f:
                self.classes = [line.strip() for line in f]
            self.update_classes_list()

    def update_classes_list(self):
        self.classes_listbox.configure(state="normal")
        self.classes_listbox.delete("1.0", "end")
        for idx, cls in enumerate(self.classes):
            self.classes_listbox.insert("end", f"{idx}: {cls}\n")
        self.classes_listbox.configure(state="disabled")

    def select_class(self, event):
        try:
            index = int(self.classes_listbox.get("current linestart", "current lineend").split(":")[0])
            if 0 <= index < len(self.classes):
                self.current_class = index

                self.classes_listbox.configure(state="normal")
                self.classes_listbox.tag_remove("highlight", "1.0", "end")
                start = f"{index + 1}.0"
                end = f"{index + 1}.end"
                self.classes_listbox.tag_add("highlight", start, end)
                self.classes_listbox.tag_configure("highlight", background="red")
                self.classes_listbox.configure(state="disabled")
        except Exception as e:
            print("Error selecting class:", e)

    def display_image(self):
        if self.current_index < len(self.images):
            image_path = self.images[self.current_index]
            self.image_name_label.configure(text=os.path.basename(image_path))

            image = Image.open(image_path)
            image = image.resize((640, 640), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
            self.canvas.image = photo

            self.load_annotations(image_path)

            self.canvas.bind("<Button-1>", self.annotation_click)
            self.canvas.bind("<Motion>", self.update_guidelines)
            self.canvas.bind("<Button-3>", self.delete_box)
            self.canvas.bind_all("<MouseWheel>", self.scroll_images)

    def annotation_click(self, event):
        if self.start_x is None and self.start_y is None:
            self.start_x, self.start_y = event.x, event.y
        else:
            end_x, end_y = event.x, event.y

            # Create a rectangle while placing it dynamically
            if self.temp_box:
                self.canvas.delete(self.temp_box)
            self.temp_box = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="blue", dash=(3, 3), width=2)

            canvas_width = 640
            canvas_height = 640

            x_center = (self.start_x + end_x) / 2 / canvas_width
            y_center = (self.start_y + end_y) / 2 / canvas_height
            width = abs(end_x - self.start_x) / canvas_width
            height = abs(end_y - self.start_y) / canvas_height

            image_name = os.path.basename(self.images[self.current_index])
            annotation_path = os.path.join(self.image_folder, f"{os.path.splitext(image_name)[0]}.txt")

            # Explicitly write the annotation with a newline
            with open(annotation_path, "a") as f:
                f.write(f"{self.current_class} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

            box_id = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", width=2)
            text_id = self.canvas.create_text(self.start_x + 5, self.start_y + 10, text=self.classes[self.current_class], anchor="nw", fill="white", font=("Arial", 10))
            self.box_ids.append((box_id, text_id, annotation_path))

            # Clear temporary data
            self.start_x, self.start_y = None, None
            self.clear_guidelines()

    def update_guidelines(self, event):
        self.clear_guidelines()
        if self.start_x is not None and self.start_y is not None:
            if self.temp_box:
                self.canvas.delete(self.temp_box)
            self.temp_box = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="blue", dash=(3, 3), width=2)

        self.temp_lines.append(self.canvas.create_line(event.x, 0, event.x, 640, fill="blue", dash=(4, 2)))
        self.temp_lines.append(self.canvas.create_line(0, event.y, 640, event.y, fill="blue", dash=(4, 2)))

    def clear_guidelines(self):
        for line in self.temp_lines:
            self.canvas.delete(line)
        self.temp_lines = []

    def load_annotations(self, image_path):
        annotation_path = os.path.splitext(image_path)[0] + ".txt"
        if os.path.exists(annotation_path):
            with open(annotation_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:  # Ensure the line contains all expected values
                        cls = int(parts[0])  # Class number
                        if 0 <= cls < len(self.classes):  # Check if class index is valid
                            x_center, y_center, width, height = map(float, parts[1:])

                            canvas_width = 640
                            canvas_height = 640

                            x1 = (x_center - width / 2) * canvas_width
                            y1 = (y_center - height / 2) * canvas_height
                            x2 = (x_center + width / 2) * canvas_width
                            y2 = (y_center + height / 2) * canvas_height

                            box_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
                            text_id = self.canvas.create_text(x1 + 5, y1 + 10, text=self.classes[cls], anchor="nw", fill="white", font=("Arial", 10))
                            self.box_ids.append((box_id, text_id, annotation_path))
                        else:
                            print(f"Invalid class ID {cls} in annotation file: {annotation_path}")

    def delete_box(self, event):
    # Find the canvas items at the clicked position
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)

        for clicked_item in clicked_items:
            for box_id, text_id, annotation_path in self.box_ids:
                if clicked_item in (box_id, text_id):
                    # Remove the box and label from the canvas
                    self.canvas.delete(box_id)
                    self.canvas.delete(text_id)
                    self.box_ids.remove((box_id, text_id, annotation_path))

                    # Update the corresponding annotation file
                    if os.path.exists(annotation_path):
                        with open(annotation_path, "r") as f:
                            lines = f.readlines()

                        updated_lines = []
                        for line in lines:
                            parts = line.strip().split()
                            if len(parts) == 5:  # Ensure the annotation line is valid
                                cls, x_center, y_center, width, height = map(float, parts)
                                canvas_width, canvas_height = 640, 640

                                # Recalculate box coordinates in canvas terms
                                x1 = (x_center - width / 2) * canvas_width
                                y1 = (y_center - height / 2) * canvas_height
                                x2 = (x_center + width / 2) * canvas_width
                                y2 = (y_center + height / 2) * canvas_height

                                # Check if the current annotation matches the deleted box
                                if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
                                    updated_lines.append(line)

                        # Write the updated annotations back to the file
                        with open(annotation_path, "w") as f:
                            f.writelines(updated_lines)
                            f.flush()  # Force the OS to flush the buffer
                            os.fsync(f.fileno())  # Ensure the write operation is completed on disk
                    # Exit after handling the clicked item
                    return

    def scroll_images(self, event):
        if event.delta > 0:
            self.current_index = max(0, self.current_index - 1)
        else:
            self.current_index = min(len(self.images) - 1, self.current_index + 1)
        self.display_image()