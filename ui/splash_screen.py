import customtkinter as ctk
import threading
from PIL import Image
import os

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        # Configure window
        self.title("")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(fg_color=("gray95", "gray10"))

        # Remove window decorations
        self.overrideredirect(True)

        # Center window
        self.center_window()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="AI Quiz App",
            font=("Helvetica", 28, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 0))

        # Loading animation frame
        self.loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.loading_frame.grid(row=1, column=0, sticky="nsew")
        self.loading_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.loading_frame)
        self.progress_bar.grid(row=1, column=0, padx=30, pady=10)
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.loading_frame,
            text="Loading AI Model...",
            font=("Helvetica", 14)
        )
        self.status_label.grid(row=2, column=0, pady=5)

        # Version label
        self.version_label = ctk.CTkLabel(
            self.main_frame,
            text="v1.0.0",
            font=("Helvetica", 12),
            text_color="gray60"
        )
        self.version_label.grid(row=2, column=0, pady=(0, 10))

        # Start progress animation
        self.progress_value = 0
        self.update_progress()

        # Bring to front
        self.lift()
        self.focus_force()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def update_progress(self):
        """Update the progress bar animation."""
        if self.progress_value < 0.95:
            # Slow down progress as we approach 0.95 to simulate model loading
            if self.progress_value < 0.3:
                increment = 0.02  # Fast at beginning
            elif self.progress_value < 0.6:
                increment = 0.01  # Medium in middle
            else:
                increment = 0.005  # Slow near end

            self.progress_value += increment
            self.progress_bar.set(self.progress_value)

            # Update status text based on progress
            if self.progress_value < 0.3:
                self.update_status("Initializing application...")
            elif self.progress_value < 0.6:
                self.update_status("Loading AI model...")
            elif self.progress_value < 0.8:
                self.update_status("Preparing question database...")
            else:
                self.update_status("Almost ready...")

            self.after(50, self.update_progress)

    def update_status(self, text: str):
        """Update the status text."""
        self.status_label.configure(text=text)

    def finish(self):
        """Complete the loading animation and destroy the window."""
        self.progress_bar.set(1)
        self.after(500, self.destroy)