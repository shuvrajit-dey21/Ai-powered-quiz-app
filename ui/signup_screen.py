import customtkinter as ctk
import os
import json
import hashlib
import logging
import random
from typing import Callable
from datetime import datetime
from PIL import Image, ImageDraw

logger = logging.getLogger('QuizApp')

class SignupScreen(ctk.CTkFrame):
    def __init__(self, master, on_signup_success: Callable, on_login_click: Callable):
        super().__init__(master)

        self.on_signup_success = on_signup_success
        self.on_login_click = on_login_click

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Create UI elements
        self.create_signup_form()

    def create_signup_form(self):
        """Create signup form with username, email, and password fields."""
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
            text="Join our community of quiz enthusiasts",
            font=("Helvetica", 14),
            text_color="white"
        )
        tagline.grid(row=1, column=0)

        # Benefits list
        benefits_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        benefits_frame.grid(row=0, column=0)

        benefits = [
            "✓ Create your personal profile",
            "✓ Track your quiz history",
            "✓ Compete with other users",
            "✓ Access exclusive AI-generated content"
        ]

        for i, benefit in enumerate(benefits):
            benefit_label = ctk.CTkLabel(
                benefits_frame,
                text=benefit,
                font=("Helvetica", 14),
                text_color="white"
            )
            benefit_label.grid(row=i, column=0, sticky="w", pady=5)

        # Right side - Signup form
        right_panel = ctk.CTkFrame(self, fg_color=("#f9f9f9", "#2b2b2b"))
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Signup form container
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.grid(row=0, column=0)

        # Title
        title = ctk.CTkLabel(
            form_container,
            text="Create Account",
            font=("Helvetica", 32, "bold")
        )
        title.grid(row=0, column=0, pady=(20, 10))

        # Subtitle
        subtitle = ctk.CTkLabel(
            form_container,
            text="Join our quiz community and test your knowledge",
            font=("Helvetica", 16),
            text_color=("gray40", "gray60")
        )
        subtitle.grid(row=1, column=0, pady=(0, 30))

        # Signup form frame
        form_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=50)
        form_frame.grid_columnconfigure(0, weight=1)

        # Username field with icon
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
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
            placeholder_text="Choose a username",
            border_width=1,
            corner_radius=8
        )
        self.username_entry.grid(row=1, column=0, pady=(0, 15))

        # Email field with icon
        email_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        email_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        email_frame.grid_columnconfigure(1, weight=1)

        email_icon = ctk.CTkLabel(
            email_frame,
            text="✉️",  # Email icon emoji
            font=("Helvetica", 20)
        )
        email_icon.grid(row=0, column=0, padx=(0, 10))

        email_label = ctk.CTkLabel(
            email_frame,
            text="Email",
            font=("Helvetica", 14, "bold")
        )
        email_label.grid(row=0, column=1, sticky="w")

        self.email_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            height=45,
            placeholder_text="Enter your email",
            border_width=1,
            corner_radius=8
        )
        self.email_entry.grid(row=3, column=0, pady=(0, 15))

        # Password field with icon
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.grid(row=4, column=0, sticky="ew", pady=(0, 5))
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
            placeholder_text="Create a password",
            show="•",
            border_width=1,
            corner_radius=8
        )
        self.password_entry.grid(row=5, column=0, pady=(0, 15))

        # Confirm password field with icon
        confirm_password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        confirm_password_frame.grid(row=6, column=0, sticky="ew", pady=(0, 5))
        confirm_password_frame.grid_columnconfigure(1, weight=1)

        confirm_password_icon = ctk.CTkLabel(
            confirm_password_frame,
            text="🔒",  # Lock icon emoji
            font=("Helvetica", 20)
        )
        confirm_password_icon.grid(row=0, column=0, padx=(0, 10))

        confirm_password_label = ctk.CTkLabel(
            confirm_password_frame,
            text="Confirm Password",
            font=("Helvetica", 14, "bold")
        )
        confirm_password_label.grid(row=0, column=1, sticky="w")

        self.confirm_password_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            height=45,
            placeholder_text="Confirm your password",
            show="•",
            border_width=1,
            corner_radius=8
        )
        self.confirm_password_entry.grid(row=7, column=0, pady=(0, 10))

        # Error message label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red",
            font=("Helvetica", 12)
        )
        self.error_label.grid(row=8, column=0, pady=(0, 20))

        # Terms and conditions checkbox
        terms_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        terms_frame.grid(row=9, column=0, sticky="w", pady=(5, 15))

        self.terms_var = ctk.BooleanVar(value=False)
        terms_checkbox = ctk.CTkCheckBox(
            terms_frame,
            text="I agree to the Terms and Conditions",
            variable=self.terms_var,
            font=("Helvetica", 12),
            checkbox_width=20,
            checkbox_height=20
        )
        terms_checkbox.grid(row=0, column=0)

        # Signup button with gradient effect
        signup_button = ctk.CTkButton(
            form_frame,
            text="Create Account",
            command=self.signup,
            width=320,
            height=45,
            corner_radius=8,
            font=("Helvetica", 14, "bold"),
            fg_color="#3498db",  # Blue color
            hover_color="#2980b9"  # Darker blue on hover
        )
        signup_button.grid(row=10, column=0, pady=(0, 20))

        # Divider with "OR" text
        divider_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        divider_container.grid(row=11, column=0, sticky="ew", pady=20)
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

        # Social signup buttons (placeholders)
        social_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        social_frame.grid(row=12, column=0, pady=(0, 20))

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

        # Login link with enhanced styling
        login_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        login_frame.grid(row=13, column=0, pady=(10, 0))

        ctk.CTkLabel(
            login_frame,
            text="Already have an account?",
            font=("Helvetica", 12)
        ).grid(row=0, column=0)

        login_link = ctk.CTkButton(
            login_frame,
            text="Sign In",
            command=self.on_login_click,
            fg_color="transparent",
            hover_color=("gray90", "gray30"),
            text_color=("#3498db", "#3498db"),
            font=("Helvetica", 12, "bold"),
            width=60
        )
        login_link.grid(row=0, column=1)

        # Add a prominent button to go to login page
        back_to_login_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        back_to_login_frame.grid(row=3, column=0, pady=(20, 0))

        back_to_login_button = ctk.CTkButton(
            back_to_login_frame,
            text="← Back to Login",
            command=self.on_login_click,
            fg_color="#7f8c8d",  # Gray color
            hover_color="#636e72",  # Darker gray on hover
            text_color="white",
            width=150,
            height=35,
            corner_radius=8,
            font=("Helvetica", 14)
        )
        back_to_login_button.grid(row=0, column=0, padx=10, pady=5)

    def create_decorative_background(self):
        """Create a decorative background with random shapes."""
        # Create a blank image with a gradient background
        width, height = 600, 800
        image = Image.new("RGB", (width, height), color=(142, 68, 173))  # Purple background

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Add a gradient overlay
        for y in range(height):
            # Create a gradient from purple to dark blue
            r = int(142 + (41 - 142) * (y / height))
            g = int(68 + (128 - 68) * (y / height))
            b = int(173 + (185 - 173) * (y / height))
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

    def signup(self):
        """Register a new user."""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate inputs
        if not username or not email or not password or not confirm_password:
            self.error_label.configure(text="Please fill in all fields")
            return

        if password != confirm_password:
            self.error_label.configure(text="Passwords do not match")
            return

        if len(password) < 6:
            self.error_label.configure(text="Password must be at least 6 characters")
            return

        # Simple email validation
        if "@" not in email or "." not in email:
            self.error_label.configure(text="Please enter a valid email address")
            return

        # Check terms and conditions
        if not self.terms_var.get():
            self.error_label.configure(text="You must agree to the Terms and Conditions")
            return

        try:
            # Create users directory if it doesn't exist
            users_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data'
            )
            os.makedirs(users_dir, exist_ok=True)

            users_file = os.path.join(users_dir, 'users.json')

            # Load existing users or create empty dict
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
            else:
                users = {}

            # Check if username already exists
            if username in users:
                self.error_label.configure(text="Username already taken")
                return

            # Check if email already exists
            for user in users.values():
                if user.get('email') == email:
                    self.error_label.configure(text="Email already registered")
                    return

            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Create new user
            users[username] = {
                'email': email,
                'password': hashed_password,
                'joined_date': datetime.now().isoformat(),
                'quiz_history': [],
                'total_quizzes': 0,
                'best_score': 0
            }

            # Save to file
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=4)

            # Signup successful
            logger.info(f"New user registered: {username}")
            self.error_label.configure(text="")
            self.on_signup_success(username)

        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            self.error_label.configure(text="An error occurred. Please try again.")

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