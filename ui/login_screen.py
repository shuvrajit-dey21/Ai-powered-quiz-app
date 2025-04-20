import customtkinter as ctk
import os
import json
import hashlib
import logging
import random
from typing import Callable
from PIL import Image, ImageDraw

logger = logging.getLogger('QuizApp')

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success: Callable, on_signup_click: Callable):
        super().__init__(master)

        self.on_login_success = on_login_success
        self.on_signup_click = on_signup_click

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Create UI elements
        self.create_login_form()

    def create_login_form(self):
        """Create login form with username and password fields."""
        # Create a two-column layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left side - Decorative panel
        left_panel = ctk.CTkFrame(self, corner_radius=0)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Create a decorative background with random shapes
        bg_image = self.create_decorative_background()
        bg_label = ctk.CTkLabel(left_panel, text="", image=bg_image)
        bg_label.grid(row=0, column=0, sticky="nsew")

        # App logo/name on top of the background
        logo_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="n", pady=(50, 0))

        app_name = ctk.CTkLabel(
            logo_frame,
            text="AI Quiz App",
            font=("Helvetica", 36, "bold"),
            text_color="white"
        )
        app_name.grid(row=0, column=0, pady=10)

        tagline = ctk.CTkLabel(
            logo_frame,
            text="Test your knowledge with AI-powered questions",
            font=("Helvetica", 14),
            text_color="white"
        )
        tagline.grid(row=1, column=0)

        # Features list
        features_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        features_frame.grid(row=0, column=0)

        features = [
            "✓ Multiple quiz categories",
            "✓ AI-generated questions",
            "✓ Track your progress",
            "✓ Challenge yourself with different difficulty levels"
        ]

        for i, feature in enumerate(features):
            feature_label = ctk.CTkLabel(
                features_frame,
                text=feature,
                font=("Helvetica", 14),
                text_color="white"
            )
            feature_label.grid(row=i, column=0, sticky="w", pady=5)

        # Right side - Login form
        right_panel = ctk.CTkFrame(self, fg_color=("#f9f9f9", "#2b2b2b"))
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Login form container
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.grid(row=0, column=0)

        # Title
        title = ctk.CTkLabel(
            form_container,
            text="Welcome Back!",
            font=("Helvetica", 32, "bold")
        )
        title.grid(row=0, column=0, pady=(20, 10))

        # Subtitle
        subtitle = ctk.CTkLabel(
            form_container,
            text="Sign in to continue your quiz journey",
            font=("Helvetica", 16),
            text_color=("gray40", "gray60")
        )
        subtitle.grid(row=1, column=0, pady=(0, 30))

        # Login form frame
        form_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=50)
        form_frame.grid_columnconfigure(0, weight=1)

        # Username field with icon
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        username_frame.grid_columnconfigure(1, weight=1)

        username_icon = ctk.CTkLabel(
            username_frame,
            text="👤",  # User icon emoji
            font=("Helvetica", 20)
        )
        username_icon.grid(row=0, column=0, padx=(0, 10))

        username_label = ctk.CTkLabel(
            username_frame,
            text="Username",
            font=("Helvetica", 14, "bold")
        )
        username_label.grid(row=0, column=1, sticky="w")

        self.username_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            height=45,
            placeholder_text="Enter your username",
            border_width=1,
            corner_radius=8
        )
        self.username_entry.grid(row=1, column=0, pady=(0, 20))

        # Password field with icon
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        password_frame.grid_columnconfigure(1, weight=1)

        password_icon = ctk.CTkLabel(
            password_frame,
            text="🔒",  # Lock icon emoji
            font=("Helvetica", 20)
        )
        password_icon.grid(row=0, column=0, padx=(0, 10))

        password_label = ctk.CTkLabel(
            password_frame,
            text="Password",
            font=("Helvetica", 14, "bold")
        )
        password_label.grid(row=0, column=1, sticky="w")

        self.password_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            height=45,
            placeholder_text="Enter your password",
            show="•",
            border_width=1,
            corner_radius=8
        )
        self.password_entry.grid(row=3, column=0, pady=(0, 10))

        # Error message label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red",
            font=("Helvetica", 12)
        )
        self.error_label.grid(row=4, column=0, pady=(0, 20))

        # Remember me checkbox
        remember_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        remember_frame.grid(row=5, column=0, sticky="w", pady=(5, 15))

        self.remember_var = ctk.BooleanVar(value=False)
        remember_checkbox = ctk.CTkCheckBox(
            remember_frame,
            text="Remember me",
            variable=self.remember_var,
            font=("Helvetica", 12),
            checkbox_width=20,
            checkbox_height=20
        )
        remember_checkbox.grid(row=0, column=0)

        # Login button with gradient effect
        login_button = ctk.CTkButton(
            form_frame,
            text="Sign In",
            command=self.login,
            width=320,
            height=45,
            corner_radius=8,
            font=("Helvetica", 14, "bold"),
            fg_color="#3498db",  # Blue color
            hover_color="#2980b9"  # Darker blue on hover
        )
        login_button.grid(row=6, column=0, pady=(0, 20))

        # Divider with "OR" text
        divider_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        divider_container.grid(row=7, column=0, sticky="ew", pady=20)
        divider_container.grid_columnconfigure(0, weight=1)
        divider_container.grid_columnconfigure(2, weight=1)

        left_divider = ctk.CTkFrame(divider_container, height=1, fg_color="gray70")
        left_divider.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            divider_container,
            text="OR",
            font=("Helvetica", 12),
            text_color="gray70"
        ).grid(row=0, column=1, padx=10)

        right_divider = ctk.CTkFrame(divider_container, height=1, fg_color="gray70")
        right_divider.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        # Social login buttons (placeholders)
        social_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        social_frame.grid(row=8, column=0, pady=(0, 20))

        google_btn = ctk.CTkButton(
            social_frame,
            text="G",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#DB4437",
            hover_color="#C53929",
            font=("Helvetica", 16, "bold")
        )
        google_btn.grid(row=0, column=0, padx=10)

        facebook_btn = ctk.CTkButton(
            social_frame,
            text="f",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#4267B2",
            hover_color="#365899",
            font=("Helvetica", 16, "bold")
        )
        facebook_btn.grid(row=0, column=1, padx=10)

        twitter_btn = ctk.CTkButton(
            social_frame,
            text="t",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#1DA1F2",
            hover_color="#0c85d0",
            font=("Helvetica", 16, "bold")
        )
        twitter_btn.grid(row=0, column=2, padx=10)

        # Sign up link
        signup_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        signup_frame.grid(row=9, column=0, pady=(10, 0))

        ctk.CTkLabel(
            signup_frame,
            text="Don't have an account?",
            font=("Helvetica", 12)
        ).grid(row=0, column=0)

        signup_link = ctk.CTkButton(
            signup_frame,
            text="Sign Up",
            command=self.on_signup_click,
            fg_color="transparent",
            hover_color=("gray90", "gray30"),
            text_color=("#3498db", "#3498db"),
            font=("Helvetica", 12, "bold"),
            width=60
        )
        signup_link.grid(row=0, column=1)

        # Add a prominent button to go to signup page
        create_account_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        create_account_frame.grid(row=3, column=0, pady=(20, 0))

        create_account_button = ctk.CTkButton(
            create_account_frame,
            text="Create New Account →",
            command=self.on_signup_click,
            fg_color="#27ae60",  # Green color
            hover_color="#219653",  # Darker green on hover
            text_color="white",
            width=200,
            height=40,
            corner_radius=8,
            font=("Helvetica", 14, "bold")
        )
        create_account_button.grid(row=0, column=0, padx=10, pady=5)

    def login(self):
        """Validate login credentials and log user in."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return

        try:
            users_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'users.json'
            )

            if not os.path.exists(users_file):
                self.error_label.configure(text="No users registered. Please sign up first.")
                return

            with open(users_file, 'r') as f:
                users = json.load(f)

            if username not in users:
                self.error_label.configure(text="Invalid username or password")
                return

            user_data = users[username]
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            if hashed_password != user_data['password']:
                self.error_label.configure(text="Invalid username or password")
                return

            # Login successful
            self.error_label.configure(text="")
            logger.info(f"User {username} logged in successfully")
            self.on_login_success(username)

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            self.error_label.configure(text="An error occurred. Please try again.")

    def create_decorative_background(self):
        """Create a decorative background with random shapes."""
        # Create a blank image with a gradient background
        width, height = 600, 800
        image = Image.new("RGB", (width, height), color=(52, 152, 219))  # Blue background

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Add a gradient overlay
        for y in range(height):
            # Create a gradient from blue to purple
            r = int(52 + (142 - 52) * (y / height))
            g = int(152 + (68 - 152) * (y / height))
            b = int(219 + (173 - 219) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Add random shapes for decoration
        shapes = 15
        for _ in range(shapes):
            # Random position and size
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 100)

            # Random shape type (circle or rectangle)
            shape_type = random.choice(["circle", "rectangle"])

            # Random color (semi-transparent white)
            opacity = random.randint(10, 50)
            color = (255, 255, 255, opacity)

            if shape_type == "circle":
                draw.ellipse(
                    [(x - size//2, y - size//2), (x + size//2, y + size//2)],
                    fill=None,
                    outline=(255, 255, 255, opacity),
                    width=2
                )
            else:
                draw.rectangle(
                    [(x - size//2, y - size//2), (x + size//2, y + size//2)],
                    fill=None,
                    outline=(255, 255, 255, opacity),
                    width=2
                )

        # Convert to CTkImage
        return ctk.CTkImage(light_image=image, dark_image=image, size=(600, 800))

    def show_error(self, message: str):
        """Show error message in a popup."""
        try:
            dialog = ctk.CTkInputDialog(
                text=message,
                title="Error",
                button_text="OK"
            )
            dialog.geometry("300x150")
            dialog._input_entry.grid_remove()
            dialog.wait_window()
        except Exception as e:
            # Fallback in case CTkInputDialog doesn't support button_text
            logger.error(f"Dialog error: {str(e)}")
            messagebox = ctk.CTkToplevel(self)
            messagebox.title("Error")
            messagebox.geometry("300x150")
            messagebox.grab_set()

            ctk.CTkLabel(
                messagebox,
                text=message,
                wraplength=250
            ).pack(pady=20)

            ctk.CTkButton(
                messagebox,
                text="OK",
                command=messagebox.destroy
            ).pack(pady=10)

            messagebox.wait_window()