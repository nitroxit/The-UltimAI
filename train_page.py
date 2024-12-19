import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
from pathlib import Path
import yaml
import subprocess
import threading
from tkinter import END, Text


class TrainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.preferred_geometry = "900x980"

        ctk.CTkLabel(self, text="Train Page", font=("Arial", 16)).pack(pady=20)

        self.folder_path = None
        self.yaml_file_path = Path(__file__).parent / "training/data.yaml"  # Points to ./images/data.yaml
        self.yaml_data = None
        self.slider_value = ctk.DoubleVar(value=80)  # Default to 80%

        ctk.CTkButton(self, text="Choose Dataset Folder", command=self.choose_folder).pack(pady=10)

        self.slider_label = ctk.CTkLabel(self, text="Training Data Split: 80%")
        self.slider_label.pack(pady=5)

        self.slider = ctk.CTkSlider(self, from_=0, to=100, variable=self.slider_value, command=self.update_slider_label)
        self.slider.pack(pady=5)

        ctk.CTkButton(self, text="Split Dataset", command=self.split_dataset).pack(pady=10)

        ctk.CTkButton(self, text="Back to Main Menu", command=lambda: controller.show_page("MainPage")).pack(pady=10)

        # YAML Configuration Section
        self.yaml_editor_frame = ctk.CTkFrame(self)
        self.yaml_editor_frame.pack(fill="x", pady=20)

        self.yaml_status_label = ctk.CTkLabel(self.yaml_editor_frame, text="Checking for data.yaml in ./training...")
        self.yaml_status_label.pack()

        self.check_and_load_yaml()

    def choose_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            messagebox.showinfo("Folder Selected", f"Selected folder: {self.folder_path}")

    def update_slider_label(self, value):
        self.slider_label.configure(text=f"Training Data Split: {int(float(value))}%")

    def split_dataset(self):
        if not self.folder_path:
            messagebox.showerror("Error", "No folder selected. Please choose a dataset folder.")
            return

        # Prepare training and validation folders
        script_dir = Path(__file__).parent
        training_dir = script_dir / "training"
        if training_dir.exists():
            shutil.rmtree(training_dir)
        training_dir.mkdir(parents=True)
        (training_dir / "train/images").mkdir(parents=True)
        (training_dir / "train/labels").mkdir(parents=True)
        (training_dir / "valid/images").mkdir(parents=True)
        (training_dir / "valid/labels").mkdir(parents=True)

        # Get images and labels from the selected folder
        image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        label_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(".txt")]

        image_files.sort()  # Ensure matching order
        label_files.sort()

        if len(image_files) != len(label_files):
            messagebox.showerror("Error", "Mismatch between the number of images and labels.")
            return

        # Calculate split
        total_files = len(image_files)
        split_percentage = int(self.slider_value.get())
        train_count = int(total_files * split_percentage / 100)

        # Move files to respective folders
        for i, (image_file, label_file) in enumerate(zip(image_files, label_files)):
            src_image_path = os.path.join(self.folder_path, image_file)
            src_label_path = os.path.join(self.folder_path, label_file)

            if i < train_count:
                dst_image_path = training_dir / "train/images" / image_file
                dst_label_path = training_dir / "train/labels" / label_file
            else:
                dst_image_path = training_dir / "valid/images" / image_file
                dst_label_path = training_dir / "valid/labels" / label_file

            shutil.copy2(src_image_path, dst_image_path)
            shutil.copy2(src_label_path, dst_label_path)

        messagebox.showinfo("Success", f"Dataset split complete!\nTrain: {train_count} images\nValidation: {total_files - train_count} images")

    def check_and_load_yaml(self):
        if self.yaml_file_path.exists():
            self.yaml_status_label.configure(text="data.yaml found in ./training. Loading configuration...")
            with open(self.yaml_file_path, "r") as file:
                self.yaml_data = yaml.safe_load(file)
            self.display_yaml_editor()
        else:
            self.yaml_status_label.configure(text="data.yaml not found in ./training.")
            self.clear_yaml_editor()

    def display_yaml_editor(self):
        # Clear previous editor content
        self.clear_yaml_editor()

        # Create a container frame to center the editor
        container = ctk.CTkFrame(self.yaml_editor_frame)
        container.pack(pady=20)  # Add vertical spacing

        ctk.CTkLabel(container, text="Edit data.yaml", font=("Arial", 14)).pack(pady=10)

        # Add the entries for YAML fields
        self.path_entry = self.create_yaml_entry(container, "path", self.yaml_data.get("path", ""))
        self.train_entry = self.create_yaml_entry(container, "train", self.yaml_data.get("train", ""))
        self.val_entry = self.create_yaml_entry(container, "val", self.yaml_data.get("val", ""))
        self.nc_entry = self.create_yaml_entry(container, "nc", self.yaml_data.get("nc", ""))
        self.names_entry = self.create_yaml_entry(container, "names", ", ".join(self.yaml_data.get("names", [])))

        # Add text editor fields for epochs and model name
        self.epochs_entry = self.create_yaml_entry(container, "epochs", "120")
        self.model_name_entry = self.create_yaml_entry(container, "model", "yolov8s.pt")

        # Add Save Changes and Train buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Save Changes", command=self.save_yaml).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Train Model", command=self.start_training_thread).pack(side="left", padx=10)

        # Add output box
        self.output_box = Text(container, height=15, width=80, state="normal", wrap="word")
        self.output_box.pack(pady=10)
        self.output_box.insert(END, "Training output will be displayed here...\n")
        self.output_box.config(state="disabled")  # Make it read-only

    def start_training_thread(self):
        """
        Starts the training command in a separate thread to prevent freezing.
        """
        training_thread = threading.Thread(target=self.run_training_command, daemon=True)
        training_thread.start()

    def run_training_command(self):
        """
        Runs the YOLO training command based on the user input and displays output in the box in real-time.
        """
        # Get the user input from the editor fields
        epochs = int(self.epochs_entry.get())
        model_name = self.model_name_entry.get()

        # Ensure the data.yaml path is correct
        data_path = os.path.abspath(self.yaml_file_path)

        # Specify the runs folder location
        script_dir = os.path.abspath(os.path.dirname(__file__))
        runs_dir = os.path.join(script_dir, "training")

        # Construct the YOLO training command
        command = (
            f"yolo task=detect mode=train model={model_name} data=\"{data_path}\" "
            f"epochs={epochs} imgsz=640 plots=True project=\"{runs_dir}\""
        )

        try:
            # Open a subprocess to execute the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",  # Set encoding to utf-8
                errors="replace",  # Replace problematic characters
            )

            # Enable the output box and clear previous output
            self.output_box.config(state="normal")
            self.output_box.delete(1.0, END)

            # Buffer to hold the current line being updated
            current_line = ""

            while True:
                # Read one character at a time
                char = process.stdout.read(1)
                if not char and process.poll() is not None:
                    break  # Exit loop when process ends and no more output

                if char == "\r":
                    # Carriage return: Clear current line in the text box and prepare for update
                    self.output_box.delete("end-1c linestart", "end-1c")
                    self.output_box.insert("end-1c", current_line)
                    self.output_box.see(END)  # Auto-scroll to the end
                    current_line = ""  # Reset buffer for the next update
                elif char == "\n":
                    # Newline: Finalize the current line and start a new one
                    self.output_box.insert(END, current_line + "\n")
                    self.output_box.see(END)  # Auto-scroll to the end
                    current_line = ""  # Reset buffer for the next line
                else:
                    # Accumulate characters into the current line
                    current_line += char

            # Wait for process to complete
            process.wait()

            if process.returncode == 0:
                self.output_box.insert(END, "\nTraining completed successfully!\n")
            else:
                # Capture error output from stderr
                error_output = process.stderr.read()
                self.output_box.insert(END, f"\nAn error occurred during training:\n{error_output}\n")

            self.output_box.config(state="disabled")  # Make it read-only again

        except Exception as e:
            self.output_box.config(state="normal")
            self.output_box.insert(END, f"\nAn error occurred while starting training:\n{e}\n")
            self.output_box.config(state="disabled")

    def create_yaml_entry(self, parent, label_text, default_value):
        # Create an individual field within the container
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5)

        # Label for the field
        ctk.CTkLabel(frame, text=f"{label_text}:", width=100, anchor="w").pack(side="left", padx=5)

        # Entry for the value
        entry = ctk.CTkEntry(frame, width=400)
        entry.insert(0, str(default_value))
        entry.pack(side="left", padx=5)

        return entry


    def save_yaml(self):
        if not self.yaml_file_path:
            messagebox.showerror("Error", "No YAML file to save changes to.")
            return

        # Gather updated values
        updated_yaml = {
            "path": self.path_entry.get(),
            "train": self.train_entry.get(),
            "val": self.val_entry.get(),
            # Uncomment and add this line if you want the test field
            # "test": self.test_entry.get(),
            "nc": int(self.nc_entry.get()) if self.nc_entry.get().isdigit() else self.nc_entry.get(),
            "names": [name.strip() for name in self.names_entry.get().split(",")],
        }

        # Generate custom-formatted YAML
        yaml_content = self.generate_custom_yaml(updated_yaml)

        # Write to the YAML file
        with open(self.yaml_file_path, "w") as file:
            file.write(yaml_content)

        messagebox.showinfo("Success", "data.yaml updated successfully!")

    def generate_custom_yaml(self, yaml_data):
        """
        Generates a custom-formatted YAML string from a dictionary.
        """
        lines = []

        # Add standard fields
        lines.append(f"path: {yaml_data['path']}")
        lines.append(f"train: {yaml_data['train']}")
        lines.append(f"val: {yaml_data['val']}")
        # Add test field if needed (uncomment the line below)
        # lines.append(f"test: {yaml_data.get('test', '# test: ./test/images')}")

        # Add a blank line for spacing
        lines.append("")

        # Add nc field
        lines.append(f"nc: {yaml_data['nc']}")

        # Format the names list
        names_list = ", ".join(f"'{name}'" for name in yaml_data["names"])
        lines.append(f"names: [{names_list}]")

        # Join all lines into a single string
        return "\n".join(lines)

    def clear_yaml_editor(self):
        for widget in self.yaml_editor_frame.winfo_children():
            if widget != self.yaml_status_label:
                widget.destroy()