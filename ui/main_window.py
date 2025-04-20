import customtkinter as ctk
from typing import Optional
import logging
import threading
from .quiz_screen import QuizScreen
from .admin_screen import AdminScreen
from .splash_screen import SplashScreen
from .statistics_screen import StatisticsScreen
from .login_screen import LoginScreen
from .signup_screen import SignupScreen
from .category_manager_screen import CategoryManagerScreen
from core.question_manager import QuestionManager
import json
import os
from datetime import datetime
from PIL import Image
import random

logger = logging.getLogger('QuizApp')

class MainWindow(ctk.CTk):
    def __init__(self, question_manager: QuestionManager):
        super().__init__()

        self.question_manager = question_manager
        self.current_user = None

        # Default quiz settings
        self.quiz_settings = {
            "num_questions": 10,
            "time_per_question": 30
        }

        # Show splash screen
        self.splash = SplashScreen(self)

        # Configure window
        self.title("AI-Powered Quiz App")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Configure theme
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        ctk.set_default_color_theme("blue")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize screens
        self.login_screen = None
        self.signup_screen = None
        self.content_frame = None
        self.sidebar = None
        self.quiz_screen = None
        self.admin_screen = None
        self.statistics_screen = None
        self.settings_screen = None
        self.category_manager_screen = None
        self.ai_status_label = None

        # Show login screen by default
        self.show_login_screen()

        # Check model readiness
        self.check_model_ready()

        # Start periodic check for AI model readiness
        self.after(1000, self.check_model_ready)

    def show_login_screen(self):
        """Show the login screen."""
        self.clear_all_screens()

        self.login_screen = LoginScreen(
            self,
            self.handle_login_success,
            self.show_signup_screen
        )
        self.login_screen.grid(row=0, column=0, sticky="nsew")

    def show_signup_screen(self):
        """Show the signup screen."""
        self.clear_all_screens()

        self.signup_screen = SignupScreen(
            self,
            self.handle_signup_success,
            self.show_login_screen
        )
        self.signup_screen.grid(row=0, column=0, sticky="nsew")

    def handle_login_success(self, username: str):
        """Handle successful login."""
        self.current_user = username

        # Set current user in question manager to enable user history tracking
        self.question_manager.set_current_user(username)
        logger.info(f"User {username} logged in successfully")

        self.setup_main_ui()

    def handle_signup_success(self, username: str):
        """Handle successful signup."""
        self.current_user = username

        # Set current user in question manager to enable user history tracking
        self.question_manager.set_current_user(username)
        logger.info(f"New user registered: {username}")

        self.setup_main_ui()

    def setup_main_ui(self):
        """Setup the main UI after successful authentication."""
        self.clear_all_screens()

        # Configure grid for main UI
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Create welcome banner
        self.create_welcome_banner()

        # Create category grid
        self.create_category_grid()

    def clear_all_screens(self):
        """Clear all screens from the window."""
        # Reset grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Remove all screens
        if self.login_screen:
            self.login_screen.grid_forget()
        if self.signup_screen:
            self.signup_screen.grid_forget()
        if self.content_frame:
            self.content_frame.grid_forget()
        if self.sidebar:
            self.sidebar.grid_forget()
        if self.quiz_screen:
            self.quiz_screen.grid_forget()
        if self.admin_screen:
            self.admin_screen.grid_forget()
        if self.statistics_screen:
            self.statistics_screen.grid_forget()
        if self.settings_screen:
            self.settings_screen.grid_forget()
        if self.category_manager_screen:
            self.category_manager_screen.grid_forget()

    def create_welcome_banner(self):
        """Create an animated welcome banner."""
        banner_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray90", "gray17"),
            corner_radius=15
        )
        banner_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        banner_frame.grid_columnconfigure(0, weight=1)

        # Add a subtle gradient-like effect by using nested frames
        gradient_frame = ctk.CTkFrame(
            banner_frame,
            fg_color=("gray85", "gray15"),
            corner_radius=12,
            border_width=1,
            border_color=("gray75", "gray25")
        )
        gradient_frame.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        gradient_frame.grid_columnconfigure(0, weight=1)

        # Container for text elements
        text_container = ctk.CTkFrame(gradient_frame, fg_color="transparent")
        text_container.grid(row=0, column=0, padx=20, pady=15)
        text_container.grid_columnconfigure(0, weight=1)

        # Add decorative elements
        left_decor = "✦ ✧ ✦"
        right_decor = "✦ ✧ ✦"

        if self.current_user:
            # Personalized welcome with decorations
            title_text = f"{left_decor} Welcome {self.current_user}! {right_decor}"
            title = ctk.CTkLabel(
                text_container,
                text=title_text,
                font=("Helvetica", 32, "bold"),
                text_color=("#3a7ebf", "#5eb5f7")
            )
        else:
            # Generic welcome
            title_text = f"{left_decor} Welcome to AI Quiz Challenge! {right_decor}"
            title = ctk.CTkLabel(
                text_container,
                text=title_text,
                font=("Helvetica", 32, "bold"),
                text_color=("#3a7ebf", "#5eb5f7")
            )

        title.grid(row=0, column=0, pady=(0, 5))

        # Animated subtitle with typewriter effect simulation
        subtitle_text = "Test your knowledge across various categories"
        subtitle = ctk.CTkLabel(
            text_container,
            text=subtitle_text,
            font=("Helvetica", 16),
            text_color=("gray40", "gray60")
        )
        subtitle.grid(row=1, column=0, pady=(0, 5))

        # Add a motivational quote that changes periodically
        quotes = [
            "Knowledge is power. Test yours!",
            "Challenge yourself with our quizzes!",
            "Learn something new every day.",
            "Every quiz is an opportunity to grow.",
            "The more you learn, the more you earn."
        ]

        import random
        quote_text = random.choice(quotes)

        quote = ctk.CTkLabel(
            text_container,
            text=f"\"{quote_text}\"",
            font=("Helvetica", 14, "italic"),
            text_color=("gray45", "gray55")
        )
        quote.grid(row=2, column=0, pady=(5, 0))

        # Store references to update later
        self.banner_elements = {
            "title": title,
            "subtitle": subtitle,
            "quote": quote
        }

        # Simulating animation after a delay
        self.after(500, lambda: self._animate_banner(title, subtitle, quote))

    def _animate_banner(self, title, subtitle, quote):
        """Add simple animations to the welcome banner elements."""
        # Simple "fade-in" effect by gradually increasing text opacity
        # We'll simulate this by changing text color

        # Original colors
        title_colors = ("#3a7ebf", "#5eb5f7")
        subtitle_colors = ("gray40", "gray60")
        quote_colors = ("gray45", "gray55")

        # First make elements semi-transparent
        title.configure(text_color=("gray70", "gray40"))
        subtitle.configure(text_color=("gray70", "gray40"))
        quote.configure(text_color=("gray70", "gray40"))

        # Then gradually restore their colors
        self.after(150, lambda: title.configure(text_color=title_colors))
        self.after(300, lambda: subtitle.configure(text_color=subtitle_colors))
        self.after(450, lambda: quote.configure(text_color=quote_colors))

        # Optional: Add a subtle scale animation for the title
        def _scale_up():
            current_font = title.cget("font")
            if isinstance(current_font, tuple) and len(current_font) >= 2:
                # If font is already a tuple with size
                new_size = current_font[1] + 2
                title.configure(font=(current_font[0], new_size, "bold"))
            self.after(100, _scale_down)

        def _scale_down():
            current_font = title.cget("font")
            if isinstance(current_font, tuple) and len(current_font) >= 2:
                # If font is already a tuple with size
                new_size = current_font[1] - 2
                title.configure(font=(current_font[0], new_size, "bold"))

        # Try scale animation, but catch any errors if font handling fails
        try:
            self.after(600, _scale_up)
        except:
            # Just continue if animation fails
            pass

    def create_category_grid(self):
        """Create a grid of category cards."""
        self.category_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.category_frame.grid(row=1, column=0, sticky="nsew")
        self.category_frame.grid_columnconfigure((0,1,2), weight=1)

        categories = self.question_manager.get_categories()

        # Enhanced category colors with better contrast and visual appeal
        colors = {
            "Science": {"bg": "#FF6B6B", "icon": "🔬"},
            "History": {"bg": "#4ECDC4", "icon": "📜"},
            "Geography": {"bg": "#45B7D1", "icon": "🌍"},
            "Literature": {"bg": "#96CEB4", "icon": "📚"},
            "Movies": {"bg": "#FFEEAD", "icon": "🎬"},
            "Sports": {"bg": "#D4A5A5", "icon": "⚽"},
            "Technology": {"bg": "#9B59B6", "icon": "💻"},
            "Music": {"bg": "#3498DB", "icon": "🎵"}
        }

        # Add default color for any category not in our predefined list
        default_color = {"bg": "#1ABC9C", "icon": "❓"}

        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3

            category_data = colors.get(category, default_color)
            card = self.create_category_card(
                category,
                category_data["bg"],
                category_data["icon"]
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def create_category_card(self, category: str, color: str, icon: str):
        """Create a category card with hover effects and animations."""
        # Main card container
        card = ctk.CTkFrame(
            self.category_frame,
            fg_color=color,
            corner_radius=15,
            border_width=2,
            border_color=self._darken_color(color)
        )
        card.grid_columnconfigure(0, weight=1)

        # Add hover effect
        card.bind("<Enter>", lambda e, c=card: self._on_card_hover(c, True, color))
        card.bind("<Leave>", lambda e, c=card: self._on_card_hover(c, False, color))

        # Category header with icon
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        # Category name with icon
        name_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {category}",
            font=("Helvetica", 22, "bold"),
            text_color="white"
        )
        name_label.grid(row=0, column=0, pady=(5, 0))

        # Statistics in a separate frame with cleaner styling
        stats = self.get_category_stats(category)

        stats_frame = ctk.CTkFrame(card, fg_color=self._darken_color(color, factor=0.1), corner_radius=8)
        stats_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        # Quizzes taken
        ctk.CTkLabel(
            stats_frame,
            text="Quizzes:",
            font=("Helvetica", 12),
            text_color="white"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=2)

        ctk.CTkLabel(
            stats_frame,
            text=str(stats['quizzes']),
            font=("Helvetica", 12, "bold"),
            text_color="white"
        ).grid(row=0, column=1, sticky="e", padx=10, pady=2)

        # Best score
        ctk.CTkLabel(
            stats_frame,
            text="Best Score:",
            font=("Helvetica", 12),
            text_color="white"
        ).grid(row=1, column=0, sticky="w", padx=10, pady=2)

        ctk.CTkLabel(
            stats_frame,
            text=f"{stats['best_score']}%",
            font=("Helvetica", 12, "bold"),
            text_color="white"
        ).grid(row=1, column=1, sticky="e", padx=10, pady=2)

        # Difficulty buttons with enhanced styling
        diff_frame = ctk.CTkFrame(card, fg_color="transparent")
        diff_frame.grid(row=2, column=0, pady=(10, 10))

        difficulties = [
            ("Easy", "green", "#2ECC71"),
            ("Medium", "orange", "#F39C12"),
            ("Hard", "red", "#E74C3C")
        ]

        # Add refresh button for all categories
        refresh_frame = ctk.CTkFrame(card, fg_color="transparent")
        refresh_frame.grid(row=3, column=0, pady=(0, 15))

        refresh_btn = ctk.CTkButton(
            refresh_frame,
            text="🔄 Refresh Questions",
            fg_color="#3498DB",
            hover_color="#2980B9",
            text_color="white",
            width=180,
            height=30,
            corner_radius=8,
            font=("Helvetica", 12),
            command=lambda c=category: self.regenerate_category_questions(c)
        )
        refresh_btn.grid(row=0, column=0, padx=0)

        for i, (diff, _, btn_color) in enumerate(difficulties):
            # Create container for button with animation
            btn_container = ctk.CTkFrame(diff_frame, fg_color="transparent")
            btn_container.grid(row=0, column=i, padx=5)

            btn = ctk.CTkButton(
                btn_container,
                text=diff,
                fg_color=btn_color,
                hover_color=self._darken_color(btn_color),
                text_color="white",
                text_color_disabled="gray70",
                width=80,
                height=32,
                corner_radius=8,
                font=("Helvetica", 12, "bold"),
                command=lambda c=category, d=diff.lower(): self.start_quiz(c, d)
            )
            btn.grid(row=0, column=0, padx=0)

            # Add hover animation
            btn.bind("<Enter>", lambda e, b=btn, c=btn_color: self._on_button_hover(b, True, c))
            btn.bind("<Leave>", lambda e, b=btn, c=btn_color: self._on_button_hover(b, False, c))

        return card

    def _on_card_hover(self, card, is_hover: bool, original_color: str):
        """Handle hover animation for category cards."""
        if is_hover:
            # Lift the card slightly
            card.configure(
                border_width=3,
                fg_color=self._lighten_color(original_color)
            )
        else:
            # Return to normal
            card.configure(
                border_width=2,
                fg_color=original_color
            )

    def _on_button_hover(self, button, is_hover: bool, original_color: str):
        """Handle hover animation for difficulty buttons."""
        if is_hover:
            button.configure(
                border_width=2,
                border_color="white"
            )
        else:
            button.configure(
                border_width=0
            )

    def _darken_color(self, hex_color: str, factor: float = 0.15) -> str:
        """Darken a hex color by a factor."""
        # Skip processing for dynamic colors
        if "gray" in hex_color or hex_color.startswith(("(", "#")):
            return hex_color

        try:
            # Convert to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

            # Darken
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))

            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            # If any error, return the original color
            return hex_color

    def _lighten_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Lighten a hex color by a factor."""
        # Skip processing for dynamic colors
        if "gray" in hex_color or hex_color.startswith(("(", "#")):
            return hex_color

        try:
            # Convert to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

            # Lighten
            r = min(255, int(r * (1 + factor)))
            g = min(255, int(g * (1 + factor)))
            b = min(255, int(b * (1 + factor)))

            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            # If any error, return the original color
            return hex_color

    def get_category_stats(self, category: str) -> dict:
        """Get statistics for a category."""
        try:
            stats_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'stats.json')
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                cat_stats = stats.get("categories", {}).get(category, {})
                return {
                    "quizzes": cat_stats.get("total", 0),
                    "best_score": round(cat_stats.get("best_score", 0), 1)
                }
        except Exception as e:
            logger.error(f"Error loading category stats: {str(e)}")
        return {"quizzes": 0, "best_score": 0.0}

    def create_sidebar(self):
        """Create an enhanced sidebar with icons."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Add AI status indicator at the bottom of sidebar
        self.ai_status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.ai_status_frame.grid(row=9, column=0, sticky="ew", padx=10, pady=5)

        self.ai_status_label = ctk.CTkLabel(
            self.ai_status_frame,
            text="AI Status: Loading...",
            font=("Helvetica", 12),
            text_color="orange"
        )
        self.ai_status_label.grid(row=0, column=0, sticky="w")

        # App logo/title with better styling
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=10, pady=(15, 20))

        ctk.CTkLabel(
            logo_frame,
            text="🧠 Quiz App",
            font=("Helvetica", 22, "bold"),
            text_color=("#3a7ebf", "#1f538d")
        ).grid(row=0, column=0)

        # User info with better styling
        if self.current_user:
            user_frame = ctk.CTkFrame(self.sidebar, fg_color=("gray90", "gray20"), corner_radius=8)
            user_frame.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="ew")

            ctk.CTkLabel(
                user_frame,
                text=f"👤 {self.current_user}",
                font=("Helvetica", 14),
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=8)

        # Navigation buttons with improved styling
        nav_buttons = [
            ("🏠 Home", self.show_home),
            ("📊 Statistics", self.show_statistics),
            ("📁 Categories", self.show_category_manager),
            ("⚙️ Settings", self.show_settings),
            ("👑 Admin Mode", self.open_admin_mode)
        ]

        start_row = 2 if self.current_user else 1

        # Create a container frame for nav buttons
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.grid(row=start_row, column=0, sticky="ew", pady=5)

        for i, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                nav_container,
                text=text,
                command=command,
                height=35,
                font=("Helvetica", 13),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25")
            )
            btn.grid(row=i, column=0, padx=10, pady=3, sticky="ew")

        # Separator line
        separator = ctk.CTkFrame(self.sidebar, height=1, fg_color=("gray80", "gray30"))
        separator.grid(row=start_row+1, column=0, sticky="ew", padx=10, pady=15)

        # AI Model Selection Section
        ai_section_label = ctk.CTkLabel(
            self.sidebar,
            text="🤖 AI Model Selection",
            font=("Helvetica", 14, "bold"),
            anchor="w"
        )
        ai_section_label.grid(row=start_row+2, column=0, sticky="w", padx=15, pady=(10, 5))

        # Available AI models
        available_models = [
            "distilgpt2",
            "gpt2",
            "facebook/opt-125m",
            "distilbert-base-uncased",
            "google/flan-t5-small"
        ]

        # Get current model name from question manager
        current_model = self.question_manager.ai_generator.model_name

        # Create model selection dropdown
        self.model_dropdown = ctk.CTkOptionMenu(
            self.sidebar,
            values=available_models,
            command=self.change_ai_model,
            width=180,
            height=30,
            font=("Helvetica", 12),
            dropdown_font=("Helvetica", 12)
        )
        self.model_dropdown.grid(row=start_row+3, column=0, padx=15, pady=(0, 5))

        # Set current value
        if current_model in available_models:
            self.model_dropdown.set(current_model)
        else:
            self.model_dropdown.set(available_models[0])

        # Apply button for model change
        apply_model_btn = ctk.CTkButton(
            self.sidebar,
            text="Apply Model Change",
            command=self.apply_model_change,
            height=30,
            font=("Helvetica", 12),
            fg_color="#28a745",
            hover_color="#218838"
        )
        apply_model_btn.grid(row=start_row+4, column=0, padx=15, pady=(0, 15))

        # Second separator
        separator2 = ctk.CTkFrame(self.sidebar, height=1, fg_color=("gray80", "gray30"))
        separator2.grid(row=start_row+5, column=0, sticky="ew", padx=10, pady=15)

        # Bottom buttons container
        bottom_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_container.grid(row=11, column=0, sticky="ew", pady=5)

        # Logout button
        if self.current_user:
            logout_btn = ctk.CTkButton(
                bottom_container,
                text="🚪 Logout",
                command=self.logout,
                height=35,
                font=("Helvetica", 13),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25")
            )
            logout_btn.grid(row=0, column=0, padx=10, pady=3, sticky="ew")

        # Theme toggle with better styling
        theme_btn = ctk.CTkButton(
            bottom_container,
            text="🌓 Toggle Theme",
            command=self.toggle_theme,
            height=35,
            font=("Helvetica", 13),
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray75", "gray25")
        )
        theme_btn.grid(row=1, column=0, padx=10, pady=(3, 10), sticky="ew")

    def logout(self):
        """Log out the current user and return to login screen."""
        self.current_user = None
        self.show_login_screen()

    def start_quiz(self, category: str, difficulty: str):
        """Start a quiz with selected category and difficulty."""
        try:
            # Hide content frame
            self.content_frame.grid_remove()

            # Get settings
            num_questions = self.quiz_settings["num_questions"]
            time_per_question = self.quiz_settings["time_per_question"]
            logger.info(f"Starting quiz with settings: {num_questions} questions, {time_per_question} seconds per question")

            # Create and show quiz screen
            self.quiz_screen = QuizScreen(
                self,
                self.question_manager,
                category,
                difficulty,
                num_questions,  # Use setting instead of hardcoded value
                time_per_question,  # Use setting instead of hardcoded value
                self.end_quiz
            )
            self.quiz_screen.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        except Exception as e:
            logger.error(f"Error starting quiz: {str(e)}")
            self.show_error("An error occurred while starting the quiz")

    def show_home(self):
        """Show the home screen."""
        # Clear any existing screens
        if self.quiz_screen:
            self.quiz_screen.destroy()
            self.quiz_screen = None
        if self.admin_screen:
            self.admin_screen.destroy()
            self.admin_screen = None
        if self.statistics_screen:
            self.statistics_screen.destroy()
            self.statistics_screen = None
        if self.settings_screen:
            self.settings_screen.destroy()
            self.settings_screen = None
        if self.category_manager_screen:
            self.category_manager_screen.destroy()
            self.category_manager_screen = None

        # Recreate the content frame if it doesn't exist or has been destroyed
        if not hasattr(self, 'content_frame') or not self.content_frame or not self.content_frame.winfo_exists():
            self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_rowconfigure(1, weight=1)

        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Make sure the content frame is visible
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Recreate welcome banner and category grid
        self.create_welcome_banner()
        self.create_category_grid()

        # Update the UI
        self.update_idletasks()

    def show_statistics(self):
        """Show the statistics screen."""
        self.content_frame.grid_remove()
        if self.quiz_screen:
            self.quiz_screen.destroy()
            self.quiz_screen = None
        if self.admin_screen:
            self.admin_screen.destroy()
            self.admin_screen = None
        if self.category_manager_screen:
            self.category_manager_screen.destroy()
            self.category_manager_screen = None

        self.statistics_screen = StatisticsScreen(self)
        self.statistics_screen.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_category_manager(self):
        """Show the category manager screen."""
        self.content_frame.grid_remove()
        if self.quiz_screen:
            self.quiz_screen.destroy()
            self.quiz_screen = None
        if self.admin_screen:
            self.admin_screen.destroy()
            self.admin_screen = None
        if self.statistics_screen:
            self.statistics_screen.destroy()
            self.statistics_screen = None

        self.category_manager_screen = CategoryManagerScreen(
            self,
            self.question_manager,
            self.show_home
        )
        self.category_manager_screen.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_settings(self):
        """Show the settings screen."""
        # Hide other screens
        self.content_frame.grid_remove()
        if self.quiz_screen:
            self.quiz_screen.destroy()
            self.quiz_screen = None
        if self.admin_screen:
            self.admin_screen.destroy()
            self.admin_screen = None
        if self.statistics_screen:
            self.statistics_screen.destroy()
            self.statistics_screen = None
        if self.category_manager_screen:
            self.category_manager_screen.destroy()
            self.category_manager_screen = None

        # Create settings screen
        self.settings_screen = ctk.CTkFrame(self)
        self.settings_screen.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.settings_screen.grid_columnconfigure(0, weight=1)

        # Settings header
        header = ctk.CTkFrame(self.settings_screen)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 30))

        ctk.CTkLabel(
            header,
            text="Settings",
            font=("Helvetica", 28, "bold")
        ).grid(row=0, column=0, pady=10)

        # Settings content
        content = ctk.CTkFrame(self.settings_screen)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(1, weight=1)

        # Appearance section
        ctk.CTkLabel(
            content,
            text="Appearance",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 10))

        # Theme selector
        ctk.CTkLabel(
            content,
            text="Theme:",
            font=("Helvetica", 14)
        ).grid(row=1, column=0, sticky="w", padx=20, pady=10)

        theme_var = ctk.StringVar(value="Dark" if ctk.get_appearance_mode() == "Dark" else "Light")

        theme_switch = ctk.CTkSegmentedButton(
            content,
            values=["Light", "Dark"],
            command=self._change_theme,
            variable=theme_var
        )
        theme_switch.grid(row=1, column=1, sticky="w", padx=20, pady=10)

        # Quiz settings section
        ctk.CTkLabel(
            content,
            text="Quiz Settings",
            font=("Helvetica", 18, "bold")
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(30, 10))

        # Questions per quiz
        ctk.CTkLabel(
            content,
            text="Questions per Quiz:",
            font=("Helvetica", 14)
        ).grid(row=3, column=0, sticky="w", padx=20, pady=10)

        questions_slider = ctk.CTkSlider(
            content,
            from_=5,
            to=20,
            number_of_steps=15,
            width=200
        )
        questions_slider.set(10)  # Default value
        questions_slider.grid(row=3, column=1, sticky="w", padx=20, pady=10)

        questions_label = ctk.CTkLabel(
            content,
            text="10",
            font=("Helvetica", 14)
        )
        questions_label.grid(row=3, column=1, sticky="e", padx=20, pady=10)

        # Update label when slider changes
        def update_question_label(value):
            questions_label.configure(text=str(int(value)))

        questions_slider.configure(command=update_question_label)

        # Time per question
        ctk.CTkLabel(
            content,
            text="Time per Question (seconds):",
            font=("Helvetica", 14)
        ).grid(row=4, column=0, sticky="w", padx=20, pady=10)

        time_slider = ctk.CTkSlider(
            content,
            from_=10,
            to=60,
            number_of_steps=50,
            width=200
        )
        time_slider.set(30)  # Default value
        time_slider.grid(row=4, column=1, sticky="w", padx=20, pady=10)

        time_label = ctk.CTkLabel(
            content,
            text="30",
            font=("Helvetica", 14)
        )
        time_label.grid(row=4, column=1, sticky="e", padx=20, pady=10)

        # Update label when slider changes
        def update_time_label(value):
            time_label.configure(text=str(int(value)))

        time_slider.configure(command=update_time_label)

        # Save button
        save_button = ctk.CTkButton(
            self.settings_screen,
            text="Save Settings",
            command=lambda: self._save_settings(int(questions_slider.get()), int(time_slider.get())),
            width=200,
            height=40,
            font=("Helvetica", 14, "bold")
        )
        save_button.grid(row=2, column=0, pady=30)

    def _change_theme(self, value):
        """Change the app theme."""
        ctk.set_appearance_mode(value)

    def _save_settings(self, num_questions, time_per_question):
        """Save quiz settings."""
        # Update settings
        self.quiz_settings["num_questions"] = num_questions
        self.quiz_settings["time_per_question"] = time_per_question

        # Here you would save to a settings file if needed
        logger.info(f"Settings saved: {num_questions} questions, {time_per_question} seconds per question")

        # Show confirmation
        dialog = ctk.CTkToplevel(self)
        dialog.title("Settings Saved")
        dialog.geometry("300x150")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Settings saved successfully!",
            font=("Helvetica", 14)
        ).pack(pady=20)

        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100
        ).pack(pady=10)

    def end_quiz(self):
        """End the current quiz and return to main menu."""
        if self.quiz_screen:
            self.quiz_screen.destroy()
            self.quiz_screen = None
        self.show_home()

    def open_admin_mode(self):
        """Open the admin mode screen."""
        self.content_frame.grid_remove()
        if self.quiz_screen:
            self.quiz_screen.destroy()
            self.quiz_screen = None
        if self.statistics_screen:
            self.statistics_screen.destroy()
            self.statistics_screen = None
        if self.category_manager_screen:
            self.category_manager_screen.destroy()
            self.category_manager_screen = None

        self.admin_screen = AdminScreen(
            self,
            self.question_manager,
            self.show_home
        )
        self.admin_screen.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        new_mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def change_ai_model(self, model_name: str):
        """Handle AI model selection change in dropdown."""
        # This just updates the dropdown - actual model change happens when Apply button is clicked
        logger.info(f"Selected AI model: {model_name}")

    def apply_model_change(self):
        """Apply the selected AI model change."""
        selected_model = self.model_dropdown.get()
        current_model = self.question_manager.ai_generator.model_name

        if selected_model == current_model:
            # No change needed
            return

        # Show loading dialog
        loading_dialog = ctk.CTkToplevel(self)
        loading_dialog.title("Changing AI Model")
        loading_dialog.geometry("400x200")
        loading_dialog.grab_set()
        loading_dialog.transient(self)

        # Center the dialog
        loading_dialog.update_idletasks()
        width = loading_dialog.winfo_width()
        height = loading_dialog.winfo_height()
        x = (loading_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (loading_dialog.winfo_screenheight() // 2) - (height // 2)
        loading_dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Loading message
        ctk.CTkLabel(
            loading_dialog,
            text=f"Changing AI model to {selected_model}...",
            font=("Helvetica", 14, "bold"),
            wraplength=350
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            loading_dialog,
            text="This may take a moment. Please wait.",
            font=("Helvetica", 12),
            text_color="gray60",
            wraplength=350
        ).pack(pady=(0, 15))

        # Progress bar
        progress = ctk.CTkProgressBar(loading_dialog, width=300, mode="indeterminate")
        progress.pack(pady=10)
        progress.start()

        # Function to perform the model change in the background
        def do_model_change():
            try:
                # Change the model in the AI generator
                self.question_manager.ai_generator.change_model(selected_model)

                # Update UI in the main thread
                self.after(0, lambda: self._finish_model_change(loading_dialog, True))
            except Exception as e:
                logger.error(f"Error changing AI model: {str(e)}")
                self.after(0, lambda: self._finish_model_change(loading_dialog, False, str(e)))

        # Start the model change in a separate thread
        threading.Thread(target=do_model_change, daemon=True).start()

    def _finish_model_change(self, dialog, success: bool, error_message: str = None):
        """Finish the model change process and update UI."""
        dialog.destroy()

        if success:
            # Show success message
            success_dialog = ctk.CTkToplevel(self)
            success_dialog.title("Success")
            success_dialog.geometry("300x150")
            success_dialog.grab_set()
            success_dialog.transient(self)

            ctk.CTkLabel(
                success_dialog,
                text="AI model changed successfully!",
                font=("Helvetica", 14)
            ).pack(pady=20)

            ctk.CTkButton(
                success_dialog,
                text="OK",
                command=success_dialog.destroy,
                width=100
            ).pack(pady=10)

            # Update AI status label
            self.check_model_ready()
        else:
            # Show error message
            self.show_error(f"Failed to change AI model: {error_message}")

    def regenerate_category_questions(self, category: str):
        """Regenerate questions for a specific category using AI."""
        try:
            # Show a progress dialog
            progress_dialog = ctk.CTkToplevel(self)
            progress_dialog.title("Generating Questions")
            progress_dialog.geometry("400x150")
            progress_dialog.grab_set()
            progress_dialog.transient(self)

            # Center the dialog
            progress_dialog.update_idletasks()
            width = progress_dialog.winfo_width()
            height = progress_dialog.winfo_height()
            x = (progress_dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (progress_dialog.winfo_screenheight() // 2) - (height // 2)
            progress_dialog.geometry(f"{width}x{height}+{x}+{y}")

            # Add message and progress bar
            ctk.CTkLabel(
                progress_dialog,
                text=f"Generating new {category} questions...",
                font=("Helvetica", 14)
            ).pack(pady=(20, 10))

            progress_bar = ctk.CTkProgressBar(progress_dialog, width=300, mode="indeterminate")
            progress_bar.pack(pady=10)
            progress_bar.start()

            # Function to perform the regeneration in the background
            def do_regeneration():
                try:
                    # Regenerate questions for all difficulties
                    for difficulty in ["easy", "medium", "hard"]:
                        self.question_manager.regenerate_questions(category, difficulty, 5)

                    # Update the UI
                    self.after(0, lambda: self._finish_regeneration(progress_dialog))
                except Exception as e:
                    logger.error(f"Error regenerating questions: {str(e)}")
                    self.after(0, lambda: self._show_regeneration_error(progress_dialog, str(e)))

            # Start the regeneration in a separate thread
            threading.Thread(target=do_regeneration, daemon=True).start()

        except Exception as e:
            logger.error(f"Error setting up question regeneration: {str(e)}")
            self.show_error(f"Error: {str(e)}")

    def _finish_regeneration(self, dialog):
        """Finish the regeneration process and update UI."""
        dialog.destroy()

        # Show success message
        success_dialog = ctk.CTkToplevel(self)
        success_dialog.title("Success")
        success_dialog.geometry("300x150")
        success_dialog.grab_set()
        success_dialog.transient(self)

        ctk.CTkLabel(
            success_dialog,
            text="Questions regenerated successfully!",
            font=("Helvetica", 14)
        ).pack(pady=20)

        ctk.CTkButton(
            success_dialog,
            text="OK",
            command=success_dialog.destroy,
            width=100
        ).pack(pady=10)

    def _show_regeneration_error(self, dialog, error_message):
        """Show error message when regeneration fails."""
        dialog.destroy()
        self.show_error(f"Failed to regenerate questions: {error_message}")

    def check_model_ready(self):
        """Check if the AI model is ready and update UI accordingly."""
        is_ready = self.question_manager.is_ai_ready()

        # Update AI status indicator if it exists
        if hasattr(self, 'ai_status_label') and self.ai_status_label:
            if is_ready:
                self.ai_status_label.configure(
                    text="AI Status: Ready ✓",
                    text_color="green"
                )
            else:
                self.ai_status_label.configure(
                    text="AI Status: Loading...",
                    text_color="orange"
                )

        # Handle splash screen
        if hasattr(self, 'splash') and self.splash:
            if is_ready:
                self.splash.finish()
            else:
                self.after(1000, self.check_model_ready)

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